class SVNFile(object):
	"""
	支持抽取指定SVN版本，查看改动情况
	"""

	def __init__(self, file_name):
		self.file_name = file_name
		self.all_version = []
		self.in_version = []
		self.text_list1 = []
		self.text_list2 = []
		self.temp_pos = (0, -1)

	def __repr__(self):
		return "<%s.%s(f:%s,v:%s,in;%s) at %s" % (
			self.__class__, self.__class__.__name__, self.file_name, self.all_version, self.in_version, id(self))

	def record_path(self, version, patch_data, in_versions):
		"""
		记录SVN补丁
		:param version: SVN版本
		:param patch_data:  补丁内容 {"DEL":[(行号，内容), ], "ADD":[(行号，内容), ]
		:param in_versions: 是否在选择抽取版本
		"""
		if version in self.all_version:
			self.print_warn("has record %s" % version)
			return
		if self.all_version and version < max(self.all_version):
			self.print_warn("%s has limit max" % version)
			return
		self.all_version.append(version)
		if in_versions:
			self.in_version.append(version)
		del_lines = patch_data["Del"]
		del_lines.sort(key=lambda x: x[0], reverse=True)
		add_lines = patch_data["Add"]
		add_lines.sort(key=lambda x: x[0])
		for line_no, line in del_lines:
			self._del_pos(line_no, line, in_versions)
		for line_no, line in add_lines:
			self._insert_pos(line_no, line, in_versions)

	def record_equip(self, version, lines, in_versions):
		"""
		记录SVN相同内容，用于补充查看
		:param version:  版本，需要先记录补丁
		:param lines:  [(行号，内容), ]
		:param in_versions: 是否在抽取的版本
		"""
		if version not in self.all_version:
			self.print_warn("must record patch first %s" % version)
			return
		if in_versions and version not in self.in_version:
			self.print_warn("must record patch sample inversion %s" % version)
			return
		if not in_versions and version in self.in_version:
			self.print_warn("must record patch sample inversion %s" % version)
			return
		lines.sort(key=lambda x: x[0])
		for line_no, line in lines:
			self._set_pos(line_no, line)

	def _del_pos(self, pos, line, in_versions):
		up_pos = self._find_pos(pos - 1)
		self.temp_pos = (pos - 1, up_pos)
		index = self._find_pos(pos)
		del_line = self.text_list1[index]
		if in_versions:
			del self.text_list1[index]
			del self.text_list2[index]
		else:
			self.text_list1[index] = ">"
		if del_line is not None and line != del_line:
			self.print_err("删除行%s内容不匹配%s!=%s index:%s" % (pos, line, del_line, index))

	def _insert_pos(self, pos, line, in_versions):
		index = self._find_pos(pos)
		self.temp_pos = (pos, index)
		self.text_list1.insert(index, line)
		if in_versions:
			self.text_list2.insert(index, line)
		else:
			self.text_list2.insert(index, ">")

	def _set_pos(self, pos, line):
		index = self._find_pos(pos)
		self.temp_pos = (pos, index)
		self.text_list1[index] = line
		if self.text_list2[index] != ">":
			# 如果该字段置为>说明之前版本增加的但是不在应用补丁范围内
			self.text_list2[index] = line

	def _find_pos(self, pos):
		"""
		寻找文本行号所在的列表下标，行号iPos从1开始，下标iIndex从0开始
		"""
		find_pos, find_index = self.temp_pos
		text_len = len(self.text_list1)
		diff = 1 if pos > find_pos else -1
		while find_pos != pos and find_index < text_len - diff:
			find_index += diff
			if self.text_list1[find_index] != ">":
				find_pos += diff
		if find_pos == pos:
			return find_index
		insert_length = abs(pos - find_pos)
		for i in range(insert_length):
			self.text_list1.append(None)
			self.text_list2.append(None)
		return len(self.text_list1) - 1

	def get_diff_text(self):
		test_list1 = [line if line is not None else "" for line in self.text_list1 if line != ">"]
		text_list2 = [line if line is not None else "" for line in self.text_list2 if line != ">"]
		return self.file_name, test_list1, text_list2

	def print_err(self, msg):
		print(self)
		print(msg)
		raise Exception("SVNUtil ErrData")

	def print_warn(self, msg):
		print(self)
		print(msg)


class CCOVFile(object):
	"""
	基本SVN版本，增加文本行标识，可用于做追溯，覆盖率等信息
	"""

	def __init__(self, file_name):
		self.file_name = file_name
		self.all_version_data = {}
		self.all_mark_data = {}

	def __repr__(self):
		return "<%s.%s(f:%s,v:%s) at %s" % (
			self.__class__, self.__class__.__name__, self.file_name, self.all_version_data.keys(), id(self))

	def record_patch(self, version, patch_data):
		"""
		记录SVN补丁信息
		:param version:  版本
		:param patch_data:  补丁内容，{"DEL":[(行号，内容), ], "ADD":[(行号，内容), ]
		"""
		if not patch_data:
			return
		self.all_version_data[version] = patch_data

	def record_coverage(self, version, lines, mark=1):
		"""
		记录表示信息，默认是数字，可以重载为其他形式，需要重写SortVal，多个相同版本标识优先显示
		:param version:  SVN版本
		:param lines: 行号列表
		:param mark:  这些行号增加的标识信息
		"""
		if not lines:
			return
		run_lines = self._deal_run_lines(lines, mark)
		if version in self.all_mark_data:
			run_lines = self._merge_run_lines(run_lines, self.all_mark_data[version])
		self.all_mark_data[version] = run_lines

	def get_mark_by_version(self, version):
		versions = sorted(self.all_version_data.keys())
		lines_result = []
		for mark_v, mark_list in self.all_mark_data.items():
			if mark_v > version:  # 大于指定版本，还原相关补丁到达对齐
				for deal_v in versions[::-1]:
					if deal_v <= version:
						break
					if deal_v > mark_v:
						continue
					mark_list = self._recover_patch(mark_list, self.all_version_data[deal_v])
			elif mark_v < version:  # 小于指定补丁，应用相关补丁到达对齐
				for deal_v in versions:
					if deal_v > version:
						break
					if deal_v <= mark_v:
						continue
					mark_list = self._apply_patch(mark_list, self.all_version_data[deal_v])
			lines_result = self._merge_run_lines(lines_result, mark_list)
		return lines_result

	def _deal_run_lines(self, lines, mark):
		temp_lines = sorted(lines)
		run_lines, index = [], 0
		for i in temp_lines:
			if i < 1:
				self.print_err("err cov line %s %s" % (i, lines))
				return []
			diff = i - index
			if diff == 1:
				run_lines.append(mark)
			elif diff <= 0:
				self.print_err("need sort line %s" % lines)
				return []
			else:
				run_lines.extend([0] * (diff - 1))
				run_lines.append(mark)
			index = i
		return run_lines

	def _merge_run_lines(self, lines_1, lines_2):
		lines_len_1, lines_len_2 = len(lines_1), len(lines_2)
		max_len = max(lines_len_1, lines_len_2)
		run_lines = []
		for i in range(max_len):
			if i < lines_len_1 and i < lines_len_2:
				mark = self.sort_val(lines_1[i], lines_2[i])
			elif i < lines_len_1:
				mark = lines_1[i]
			else:
				mark = lines_2[i]
			run_lines.append(mark)
		return run_lines

	def sort_val(self, val1, val2):
		if val1 == 0:
			return val2
		if val2 == 0:
			return val1
		return min(val1, val2)

	def _apply_patch(self, lines, patch):
		temp_lines = lines[::]
		temp_lines_len = len(temp_lines)
		del_lines = sorted(patch["DEL"], key=lambda x: x[0], reverse=True)
		for line_no, line in del_lines:
			if line_no < temp_lines_len:
				temp_lines.pop(line_no)
		temp_lines_len = len(temp_lines)
		add_lines = sorted(patch["ADD"], key=lambda x: x[0])
		for line_no, line in add_lines:
			if line_no >= temp_lines_len:
				break
			temp_lines.insert(line_no, 0)
		return temp_lines

	def _recover_patch(self, lines, patch_data):
		temp_lines = lines[::]
		temp_lines_len = len(temp_lines)
		del_lines = sorted(patch_data["ADD"], key=lambda x: x[0], reverse=True)
		for line_no, line in del_lines:
			if line_no < temp_lines_len:
				temp_lines.pop(line_no)
		temp_lines_len = len(temp_lines)
		add_lines = sorted(patch_data["DEL"], key=lambda x: x[0])
		for line_no, line in add_lines:
			if line_no >= temp_lines_len:
				break
			temp_lines.insert(line_no, 0)
		return temp_lines

	def print_err(self, msg):
		print(self)
		print(msg)
		raise Exception("SVNUtil ErrData")

	def print_warn(self, msg):
		print(self)
		print(msg)
