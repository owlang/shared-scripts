#! /usr/bin/perl/

die "usage:\t\tperl sum_Row_CDT.pl\tInput_CDT_File\tOutput_CDT_File\nExample:\tperl row_Normalize_CDT.pl input.cdt ouput.tab\n" unless $#ARGV == 1;
my($input, $output) = @ARGV;
open(IN, "<$input") or die "Can't open $input for reading!\n";
open(OUT, ">$output") or die "Can't open $output for reading!\n";

while(<IN>) {
	chomp;
	# Skip header
	if(/YORF/) {
        print OUT $_,"\n";
	# Split row into tokens and process
    } else {
		my @array = split(/\t/, $_);
		# Get $MAX value
		$MAX = 0;
		for ($x = 2; $x <= $#array; $x++) {
			if ($MAX < $array[$x]) {
				$MAX = $array[$x];
			}
		}
		# Scale by $MAX
		for ($x = 2; $x <= $#array; $x++) {
			$array[$x] /= $MAX;
		}
		# Write new row
		print OUT join("\t", @array),"\n";
	}
}
close IN;
close OUT;
