#!/usr/bin/python

#Usage: python youtube_data_analysis.py logfile_path index_directory SSIM_index_directory

from __future__ import print_function
import pylab
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import sys
import re
import collections
import pprint
import math

def get_extended_plot_info(logfile_path):
	resolution_list = []
	time_list = []
	num_bytes_list = []
	time_first = -1
	time_last = -1
	most_bytes_requested = -1
	with open(logfile_path) as f:
		for line in f:
			resolution = re.search("[0-9]+x([0-9]+)", line)
			time = re.search("([0-9]+):([0-9]+):([0-9]+)", line)
			byte_range = re.search("([0-9]+)-([0-9]+)", line)
			month_day = re.search("([A-Z][a-z]{2}) ([A-Z][a-z]{2})  ?([0-9]+)", line)
			resolution_list += [resolution.group(1)]
			time_sec = (int(month_day.group(3)) * 86400 + int(time.group(1)) * 2720 + int(time.group(2)) * 60 + int(time.group(3)))
			time_list += [time_sec]
			if time_first == -1:
				time_first = time_sec
			time_last = time_sec
			num_bytes = int(byte_range.group(2)) - int(byte_range.group(1))
			num_bytes_list += [num_bytes]
			if(num_bytes > most_bytes_requested):
				most_bytes_requested = num_bytes
	return (resolution_list, time_list, num_bytes_list, time_first, time_last, most_bytes_requested)

def plot_resolution(logfile_path, output_filename):
	plot_tuple = get_extended_plot_info(logfile_path)
	resolution_list = plot_tuple[0]
	time_list = plot_tuple[1]
	time_first = plot_tuple[3]
	time_last = plot_tuple[4]
	time_last_adjusted = time_last - time_first
	time_list_adjusted = []
	for i in range(0, len(time_list)):
		time_list_adjusted += [time_list[i] - time_first]
	plt.plot(time_list_adjusted, resolution_list)
	plt.xlabel('time in seconds')
	plt.ylabel('resolution')
	plt.ylim([0, 1440])
	plt.xlim([-100, time_last_adjusted + 100])
	plt.savefig(output_filename)
	os.system('eog ' + output_filename + '&')
	plt.clf()


def get_plot_info(logfile_path):
	resolution_list = []
	byte_range_list = []
	with open(logfile_path) as f:
		for line in f:
			resolution = re.search("[0-9]+x([0-9]+)", line)
			byte_range = re.search("([0-9]+-[0-9]+)", line)
			resolution_list += [resolution.group(1)]
			byte_range_list += [byte_range.group(1)]
	return (resolution_list, byte_range_list)

def get_filenames_list(directory_path):
	filenames_list = []
	for dirpath,_,filenames in os.walk(directory_path):
		for f in filenames:
			filenames_list += [os.path.abspath(os.path.join(dirpath, f))]
	return filenames_list

def get_resolution_from_filename(index_filename):
	match_object = re.search("818", index_filename)
	if match_object:
		return "818"
	match_object = re.search("546", index_filename)
	if match_object:
		return "546"
	match_object = re.search("364", index_filename)
	if match_object:
		return "364"
	match_object = re.search("272", index_filename)
	if match_object:
		return "272"
	match_object = re.search("182", index_filename)
	if match_object:
		return "182"
	match_object = re.search("110", index_filename)
	if match_object:
		return "110"
	return -1

def get_time_range(byte_range, offset_list, time_last):
	split_array = byte_range.split("-")
	range_start = long(split_array[0])
	range_end = long(split_array[1])
	offset_index = 0
	while(offset_index != len(offset_list) and range_start >= long(offset_list[offset_index][0])):
		offset_index = offset_index + 1
	if offset_index != 0:
		start_time = offset_list[offset_index - 1][1]
	else:
		start_time = "0.0"
	offset_index = 0
	while(offset_index != len(offset_list) and range_end >= long(offset_list[offset_index][0])):
		offset_index = offset_index + 1
	if offset_index != len(offset_list):
		end_time = offset_list[offset_index][1]
	else:
		end_time = str(time_last)
	return (start_time, end_time)

def plot_resolution_lines(graph_dict, time_first, time_last, output_filename):
	for resolution,time_range_list in graph_dict.iteritems():
		for time_range in time_range_list:
			plt.plot([time_range[0], time_range[1]], [resolution, resolution], color='Blue', linestyle='-', linewidth=1)
	plt.xlabel('time in video in seconds')
	plt.ylabel('resolution')
	plt.ylim([0, 1100])
	plt.xlim([time_first - 100, time_last + 100])
	plt.savefig(output_filename)
	os.system('eog ' + output_filename + '&')
	plt.clf()

def merge_time_ranges(time_range_list):
	merged_time_range_list = []
	previous_range_start = -1
	previous_range_end = -1
	previous_time_range = (previous_range_start, previous_range_end)
	for time_range in time_range_list:
		range_start = time_range[0]
		range_end = time_range[1]
		if previous_range_start == -1 or previous_range_end == -1:
			previous_range_start = range_start
			previous_range_end = range_end
			previous_time_range = (previous_range_start, previous_range_end)
		elif previous_range_end >= range_start:
			previous_time_range = (min(previous_range_start, range_start), max(previous_range_end, range_end))
			previous_range_start = previous_time_range[0]
			previous_range_end = previous_time_range[1]
		else:
			merged_time_range_list += [previous_time_range]
			previous_time_range = time_range
			previous_range_start = previous_time_range[0]
			previous_range_end = previous_time_range[1]
	if previous_range_start != -1 and previous_range_end != -1:
		merged_time_range_list += [previous_time_range]
	return merged_time_range_list


def get_merged_time_ranges(graph_dict):
	final_graph_dict = collections.defaultdict(lambda: list())
	for resolution,time_range_list in graph_dict.iteritems():
		merged_time_range_list = merge_time_ranges(time_range_list)
		final_graph_dict[resolution] = merged_time_range_list
	return final_graph_dict

def has_overlap(time_range1, time_range2):
	if(time_range1[0] > time_range2[0] and time_range1[0] < time_range2[1]):
		return True
	if(time_range1[1] > time_range2[0] and time_range1[1] < time_range2[1]):
		return True
	if(time_range2[0] > time_range1[0] and time_range2[0] < time_range1[1]):
		return True
	if(time_range2[1] > time_range1[0] and time_range2[1] < time_range1[1]):
		return True
	if(time_range2[0] == time_range1[0] and time_range2[1] == time_range1[1]):
		return True
	return False


def get_overlap(time_range1, time_range2):
	has_overlap_bool = has_overlap(time_range1, time_range2)
	if has_overlap_bool:
		return [(max(time_range1[0], time_range2[0]), min(time_range1[1], time_range2[1]))]
	else:
		return []

def get_overlap_list(time_range_list1, time_range_list2):
	overlap_time_range_list = []
	for time_range1 in time_range_list1:
		for time_range2 in time_range_list2:
			overlap_time_range_list += get_overlap(time_range1, time_range2)
	return overlap_time_range_list


def get_overlap_list_from_dictionary(graph_dict):
	overlap_time_range_list = []
	for resolution1, time_range_list1 in graph_dict.iteritems():
		for resolution2, time_range_list2 in graph_dict.iteritems():
			if resolution1 != resolution2:
				overlap_time_range_list += get_overlap_list(time_range_list1, time_range_list2)
	overlap_time_range_list.sort(key=lambda tup: tup[0])
	overlap_time_range_list = merge_time_ranges(overlap_time_range_list)
	return overlap_time_range_list


def print_overlap_percentage(graph_dict, duration, output_filename):
	overlap_time_range_list = get_overlap_list_from_dictionary(graph_dict)
	total_overlap_time = 0.0
	for time_range in overlap_time_range_list:
		total_overlap_time += float(time_range[1]) - float(time_range[0])
	output_file = open(output_filename, 'a')
	print("Overlap Percentage: " + str((total_overlap_time * 100) / duration), file=output_file)


def find_next_range_end(range_start, range_start_list, range_end):
	i = 0
	while range_start_list[i] <= range_start:
		i += 1
		if not i < len(range_start_list):
			return range_end
	return min(range_start_list[i], range_end)


def check_for_overlap(time_range, overall_overlap_ranges):
	for overlap_range in overall_overlap_ranges:
		if has_overlap(overlap_range, time_range):
			return True
	return False

def trim_overlap(time_range, range_start_list, overlap_time_range_list, range_start):
	if not check_for_overlap(time_range, overlap_time_range_list):
		return (range_start, time_range[1])
	else:
		return (range_start, find_next_range_end(range_start, range_start_list, time_range[1]))


def remove_overlap(graph_dict, time_last):
	overlap_time_range_list = get_overlap_list_from_dictionary(graph_dict)
	range_list_no_overlap = list()
	current_range_list_end_time = 0.0
	resolutions = ['818', '546', '364', '272', '182', '110']
	graph_dict_no_overlap = collections.defaultdict(lambda: list())
	range_start_list = list()
	for resolution in resolutions:
		time_range_list = graph_dict[resolution]
		for time_range in time_range_list:
			range_start_list += [time_range[0]]
	range_start_list.sort()
	while(current_range_list_end_time < time_last):
		for resolution in resolutions:
			time_range_list = graph_dict[resolution]
			time_range_index = 0
			selected_time_range = False
			if not time_range_index < len(time_range_list):
				continue
			while(time_range_list[time_range_index][0] <= current_range_list_end_time):
				if current_range_list_end_time < time_range_list[time_range_index][1]:
					range_list_no_overlap += [trim_overlap(time_range_list[time_range_index], range_start_list, overlap_time_range_list, current_range_list_end_time)]
					graph_dict_no_overlap[resolution] += [range_list_no_overlap[-1]]
					selected_time_range = True
				if selected_time_range:
					break
				time_range_index += 1
				if not time_range_index < len(time_range_list):
					break
			if selected_time_range:
				break
		current_range_list_end_time = range_list_no_overlap[-1][1]
	return get_merged_time_ranges(graph_dict_no_overlap)

def read_SSIM_index(index_directory):
	index = collections.defaultdict(lambda: list())
	filenames = get_filenames_list(index_directory)
	for filename in filenames:
		resolution = re.search("[0-9]+x([0-9]+)", filename).group(1)
		with open(filename) as index_file:
			for line in index_file:
				match_object = re.search("[0-9]+ ([0-9]+.[0-9]+) [A-Z] [0-9]+ ([0-9]+)", line)
				if match_object:
					SSIM_score = match_object.group(1)
					byte_offset = match_object.group(2)
					index[resolution] += [(byte_offset, SSIM_score)]
	for resolution, index_tup in index.iteritems():
		index[resolution].sort(key=lambda tup: tup[0])
	return index

def get_byte_range(time_range, time_byte_mapping):
	time_start = str(time_range[0])
	time_end = str(time_range[1])
	bytes_start = -1
	bytes_end = -1
	for mapping_tup in time_byte_mapping:
		if time_start == mapping_tup[1]:
			bytes_start = mapping_tup[0]
		if time_end == mapping_tup[1]:
			bytes_end = mapping_tup[0]
			break
	return (bytes_start, bytes_end)

def get_SSIM_scores_list(byte_range, SSIM_byte_mapping):
	SSIM_scores = []
	bytes_start = byte_range[0]
	bytes_end = byte_range[1]
	within_range = False
	for mapping_tup in SSIM_byte_mapping:
		if long(mapping_tup[0]) >= long(bytes_start) and long(mapping_tup[0]) <= long(bytes_end):
			within_range = True
		else:
			within_range = False
		if within_range:
			SSIM_scores += [mapping_tup[1]]
	return SSIM_scores

def get_SSIM_graph_dict(graph_dict, SSIM_dictionary, index):
	SSIM_graph_dict = collections.defaultdict(lambda: list())
	for resolution, time_range_list in graph_dict.iteritems():
		for time_range in time_range_list:
			byte_range = get_byte_range(time_range, index[resolution])
			SSIM_scores = get_SSIM_scores_list(byte_range, SSIM_dictionary[resolution])
			SSIM_graph_dict[resolution] += [(time_range, SSIM_scores)]
	return SSIM_graph_dict

def plot_SSIM_graph(SSIM_graph_dict, time_first, time_last, output_filename):
	FRAMES_PER_SECOND = 24
	SAMPLE_SIZE = 1.0/24.0
	SSIM_scores_data_points_list = list()
	time_data_points_list = list()
	sorted_SSIM_mapping = list()
	for resolution,time_ssim_mapping_list in SSIM_graph_dict.iteritems():
		sorted_SSIM_mapping += time_ssim_mapping_list
	sorted_SSIM_mapping.sort(key=lambda tup: tup[0][0])
	for time_ssim_mapping_tup in sorted_SSIM_mapping:
		time_range = time_ssim_mapping_tup[0]
		SSIM_scores = time_ssim_mapping_tup[1]
		total_time = float(time_range[1]) - float(time_range[0])
		time_range_beg = time_range[0]
		time_range_end = time_range_beg + SAMPLE_SIZE
		while(time_range_end <= float(time_range[1])):
			ssim_list_index = int((time_range_beg - time_range[0]) * FRAMES_PER_SECOND)
			if ssim_list_index >= len(SSIM_scores):
				break
			ssim_sum = 0.0
			num_ssim_scores = 0
			for i in range(ssim_list_index, ssim_list_index + int(FRAMES_PER_SECOND * SAMPLE_SIZE)):
				if i < len(SSIM_scores):
					ssim_sum += float(SSIM_scores[i])
					num_ssim_scores += 1
			average_ssim_score = ssim_sum / float(num_ssim_scores)
			SSIM_scores_data_points_list += [average_ssim_score]
			time_data_points_list += [time_range_end]
			time_range_beg += SAMPLE_SIZE
			time_range_end += SAMPLE_SIZE
	plt.plot(time_data_points_list, SSIM_scores_data_points_list, color='Blue')
	plt.xlabel('time in video in seconds')
	plt.ylabel('SSIM score')
	plt.ylim([0.60, 1.05])
	plt.xlim([time_first - 100, time_last + 100])
	plt.savefig(output_filename)
	os.system('eog ' + output_filename + '&')
	plt.clf()


def print_mean_stddev_SSIM(SSIM_graph_dict, output_filename):
	SSIM_scores_data_points_list = list()
	for resolution,time_ssim_mapping_list in SSIM_graph_dict.iteritems():
		for time_range_ssim_tup in time_ssim_mapping_list:
			SSIM_scores_data_points_list += time_range_ssim_tup[1]
	num_ssim_scores = len(SSIM_scores_data_points_list)
	sum_ssim_scores = 0.0
	for ssim_score in SSIM_scores_data_points_list:
		sum_ssim_scores += float(ssim_score)
	ssim_mean = sum_ssim_scores/num_ssim_scores
	output_file = open(output_filename, 'a')
	print("Mean SSIM score: " + str(ssim_mean), file=output_file)
	sum_ssim_mean_square_error = 0.0
	for ssim_score in SSIM_scores_data_points_list:
		sum_ssim_mean_square_error += math.pow(float(ssim_score) - ssim_mean, 2)
	stddev = math.sqrt(sum_ssim_mean_square_error / num_ssim_scores)
	print("Standard Deviation of SSIM scores: " + str(stddev), file=output_file)


def get_CDF_value(ssim_score, SSIM_scores_data_points_list):
	i = 0
	while(i < len(SSIM_scores_data_points_list)):
		if(float(SSIM_scores_data_points_list[i]) >= float(ssim_score)):
			break
		i += 1
	CDF = float(i)/len(SSIM_scores_data_points_list)
	return CDF


def plot_CDF(SSIM_graph_dict, output_filename):
	SSIM_scores_data_points_list = list()
	for resolution,time_ssim_mapping_list in SSIM_graph_dict.iteritems():
		for time_range_ssim_tup in time_ssim_mapping_list:
			SSIM_scores_data_points_list += time_range_ssim_tup[1]
	SSIM_scores_data_points_list.sort()
	SSIM_scores_x_axis_list = list()
	i = 0.0
	while(i <= 1.0):
		SSIM_scores_x_axis_list += [i]
		i += 0.001
	CDF_data_points_list = list()
	for ssim_score in SSIM_scores_x_axis_list:
		CDF_data_points_list += [get_CDF_value(ssim_score, SSIM_scores_data_points_list)]
	plt.plot(SSIM_scores_x_axis_list, CDF_data_points_list, color='Blue')
	plt.xlabel('SSIM score')
	plt.ylabel('CDF')
	plt.ylim([-.1, 1.1])
	plt.xlim([0.6, 1.0])
	plt.savefig(output_filename)
	os.system('eog ' + output_filename + '&')
	plt.clf()
	return CDF_data_points_list

def sc_get_next_resolution(resolution):
	if resolution == "":
		return "818"
	if resolution == "818":
		return "546"
	if resolution == "546":
		return "364"
	if resolution == "364":
		return "272"
	if resolution == "272":
		return "182"
	if resolution == "182":
		return "110"
	if resolution == "110":
		return "818"

def sc_plot_CDF_overlay(SSIM_index, output_filename, cdf_list):
	CDF_data_points_map = {}
	for resolution in SSIM_index:
		SSIM_index[resolution].sort()
		SSIM_scores_data_points_list = SSIM_index[resolution]
		SSIM_scores_x_axis_list = list()
		i = 0.0
		while(i <= 1.0):
			SSIM_scores_x_axis_list += [i]
			i += 0.001
		CDF_data_points_list = list()
		for ssim_score in SSIM_scores_x_axis_list:
			CDF_data_points_list += [get_CDF_value(ssim_score, SSIM_scores_data_points_list)]
		CDF_data_points_map[resolution] = CDF_data_points_list
	fig, ax = plt.subplots()
	axes = [ax, ax.twinx(), ax.twinx(), ax.twinx(), ax.twinx(), ax.twinx()]
	colors = ('Blue','Red', 'Green', 'Orange', 'Purple', 'Cyan')
	resolution = ""
	resolution = sc_get_next_resolution(resolution)
	for a, color in zip(axes, colors):
		a.plot(SSIM_scores_x_axis_list, CDF_data_points_map[resolution], color=color)
		a.set_ylim([-.1, 1.1])
		a.tick_params(axis='y', color=color)
		resolution = sc_get_next_resolution(resolution)
	a.plot(SSIM_scores_x_axis_list, cdf_list, color="Black")
	a.set_ylim([-.1, 1.1])
	a.tick_params(axis='y', color="Black")
	axes[0].set_xlabel('SSIM score')
	ax.set_xlim([0.6, 1.0])
	ax.set_ylabel('CDF')
	blue_patch = mpatches.Patch(color='blue', label='818')
	red_patch = mpatches.Patch(color='red', label='546')
	green_patch = mpatches.Patch(color='green', label='364')
	orange_patch = mpatches.Patch(color='orange', label='272')
	purple_patch = mpatches.Patch(color='purple', label='182')
	cyan_patch = mpatches.Patch(color='cyan', label='110')
	black_patch = mpatches.Patch(color='black', label='Verizon')
	plt.legend(handles=[blue_patch, red_patch, green_patch, orange_patch, purple_patch, cyan_patch, black_patch], loc='upper center', bbox_to_anchor=(0.25, 1.05),
          ncol=3, fancybox=True, shadow=True)
	plt.savefig(output_filename)
	os.system('eog ' + output_filename + '&')
	plt.clf()

def sc_read_SSIM_index(index_directory):
	index = collections.defaultdict(lambda: list())
	filenames = get_filenames_list(index_directory)
	for filename in filenames:
		resolution = re.search("[0-9]+x([0-9]+)", filename).group(1)
		with open(filename) as index_file:
			for line in index_file:
				match_object = re.search("[0-9]+ ([0-9]+.[0-9]+) [A-Z] [0-9]+ ([0-9]+)", line)
				if match_object:
					SSIM_score = match_object.group(1)
					index[resolution] += [SSIM_score]
	return index

def configure_file_system(logfile_path):
	trial_name = "unknown_trial_name"
	if not os.path.exists("./youtube_analysis_output"):
		os.system("mkdir youtube_analysis_output")
	trial_name_match_object = re.search("\.?\/?youtube_logs/([0-9A-Za-z_-]+)\.?(?:[A-Za-z]+)?", logfile_path)
	if trial_name_match_object:
		trial_name = trial_name_match_object.group(1)
	else:
		trial_name_match_object = re.search(".+\/([0-9A-Za-z_-]+)\.txt", logfile_path)
		if trial_name_match_object:
			trial_name = trial_name_match_object.group(1)
	output_filename = "./youtube_analysis_output/" + trial_name + "/"
	if not os.path.exists(output_filename):
		os.system("mkdir " + output_filename)
	return output_filename

def main():
	logfile_path = sys.argv[1]
	output_filename = configure_file_system(logfile_path)
	plot_resolution(logfile_path, output_filename + "resolution_requests.png")
	plotTuple = get_plot_info(logfile_path)
	resolution_list = plotTuple[0]
	byte_range_list = plotTuple[1]
	index_directory = sys.argv[2]
	SSIM_index_directory = sys.argv[3]
	all_files = get_filenames_list(index_directory)
	index_filenames = []
	for filename in all_files:
		match_object = re.search("[0-9]+x[0-9]+_index", filename)
		if match_object:
			index_filenames += [filename]
	time_last = -1
	index = collections.defaultdict(lambda: list()) #dictionary from resolution to sorted list of tuples (byte offset, time offset)
	for index_filename in index_filenames:
		resolution = get_resolution_from_filename(index_filename)
		with open(index_filename) as index_file:
			for line in index_file:
				offset_match_object = re.search("Byte Offset: ([0-9]+) Time Offset: ([0-9]+.[0-9]+)", line)
				if offset_match_object:
					byte_offset = offset_match_object.group(1)
					time_offset = offset_match_object.group(2)
					index[resolution] = index[resolution] + [(byte_offset, time_offset)]
				duration_match_object = re.search("Duration: ([0-9]+)", line)
				if duration_match_object:
					time_last = float(duration_match_object.group(1))/1000
	final_graph_dict = collections.defaultdict(lambda: list())
	for i,resolution_requested in enumerate(resolution_list):
		offset_list = index[resolution_requested]
		time_range = get_time_range(byte_range_list[i], offset_list, time_last)
		#print "Resolution: " + resolution_requested + " Byte Range: " + byte_range_list[i] + " Time Range: " + str(time_range[0]) + "-" + str(time_range[1])
		if(time_range[0] != "0.0" or time_range[1] != "0.0"):
			time_tuple = (float(time_range[0]), float(time_range[1]))
			final_graph_dict[resolution_requested] = final_graph_dict[resolution_requested] + [time_tuple]
	final_graph_dict = get_merged_time_ranges(final_graph_dict)
	print_overlap_percentage(final_graph_dict, time_last, output_filename + "stats.txt")
	plot_resolution_lines(final_graph_dict, 0, time_last, output_filename + "resolution_lines_with_overlap.png")
	final_graph_dict = remove_overlap(final_graph_dict, time_last)
	plot_resolution_lines(final_graph_dict, 0, time_last, output_filename + "resolution_lines_no_overlap.png")
	SSIM_dictionary = read_SSIM_index(SSIM_index_directory)
	SSIM_graph_dict = get_SSIM_graph_dict(final_graph_dict, SSIM_dictionary, index)
	print_mean_stddev_SSIM(SSIM_graph_dict,  output_filename + "stats.txt")
	cdf_list = plot_CDF(SSIM_graph_dict,  output_filename + "CDF.png")
	plot_SSIM_graph(SSIM_graph_dict, 0, time_last, output_filename + "SSIM.png")
	SSIM_index = sc_read_SSIM_index(SSIM_index_directory)
	sc_plot_CDF_overlay(SSIM_index, output_filename + "CDF_overlay.png", cdf_list)




if __name__ == '__main__':
  main()
