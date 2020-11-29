import sys


def count_GC(fastq_read):
    count = 0
    for base in fastq_read:
        if base == 'G' or base == 'C':
            count += 1
    return count * 100 / len(fastq_read)

def write_read_to_file(fastq_read_lines, file):
    file.write('\n'.join(fastq_read_lines) + '\n')


def validate_read(fastq_read, min_length, gc_bounds):
    if len(fastq_read) < min_length:
        return False
    if len(gc_bounds) == 1:
        if count_GC(fastq_read) < gc_bounds[0]:
            return False
    if len(gc_bounds) == 2:
        if count_GC(fastq_read) < gc_bounds[0] or count_GC(fastq_read) > gc_bounds[1]:
            return False
    return True

last_arg = sys.argv[len(sys.argv) - 1]
splitted_by_dots = last_arg.split('.')

MIN_LENGTH_ARG = '--min_length'
KEEP_FILTERED_ARG = '--keep_filtered'
GC_BOUNDS_ARG = '--gc_bounds'
OUTPUT_BASE_NAME_ARG = '--output_base_name'

valid_args = [MIN_LENGTH_ARG, KEEP_FILTERED_ARG, GC_BOUNDS_ARG, OUTPUT_BASE_NAME_ARG]


min_length = 0
keep_filtered = False
gc_bounds = []
input_file = sys.argv[-1]


output_base_name = '.'.join(splitted_by_dots[0 : len(splitted_by_dots) - 1])


i = 1
while i < len(sys.argv) - 1:
    if sys.argv[i] not in valid_args:
        raise ValueError('Invalid argument: ' + sys.argv[i])
    if sys.argv[i] == MIN_LENGTH_ARG:
        min_length = int(sys.argv[i + 1])
        if min_length <= 0:
            raise ValueError(MIN_LENGTH_ARG + ' must be greater than 0')
        i += 2
        continue
    if sys.argv[i] == KEEP_FILTERED_ARG:
        keep_filtered = True
        i += 1
        continue
    if sys.argv[i] == GC_BOUNDS_ARG:
        i += 1
        while sys.argv[i].isnumeric():
            gc_bounds.append(int(sys.argv[i]))
            i += 1
        if len(gc_bounds) > 2:
            raise ValueError(GC_BOUNDS_ARG + ' must contain only up to two values')
        continue
    if sys.argv[i] == OUTPUT_BASE_NAME_ARG:
        output_base_name = sys.argv[i + 1]
        i += 2
        continue

print('\n ----->>  Your setup: \n')
print(MIN_LENGTH_ARG + ' ' + str(min_length))
print(KEEP_FILTERED_ARG, keep_filtered, sep = " ")
print(GC_BOUNDS_ARG, gc_bounds, sep = " ")
print(OUTPUT_BASE_NAME_ARG + ' ' +  output_base_name)
print('your input file name: ', input_file)
print('\n ----->> Filtering: Start')

fastq = open(input_file, 'r')
passed = open(output_base_name + '__passed.fastq', 'w')
if keep_filtered:
    failed = open(output_base_name + '__failed.fastq', 'w')

lines = fastq.read().splitlines()

count_passed = 0
count_failed = 0
for i in range(0, len(lines), 4):
    fastq_read_info = lines[i : i + 4]
    if i == 0:
        print()
    if validate_read(fastq_read_info[1], min_length, gc_bounds):
        write_read_to_file(fastq_read_info, passed)
        count_passed += 1
    else:
        if keep_filtered:
            write_read_to_file(fastq_read_info, failed)
        count_failed += 1

print('\n ----->> total number of processed reads in ' + input_file + ': ' + str(len(lines) // 4))
print('\n ----->> Filtering: Finish')
print('\n ----->> number of passed reads: ' + str(count_passed))
print('\n ----->> number of failed reads: ' + str(count_failed))

percent = round(count_passed * 100 / (len(lines) // 4), 2)
print('\n ----->> percent of passed reads: ' + str(percent))

passed.close()
fastq.close()
if keep_filtered:
    failed.close()
