#! /usr/bin/perl/

die "usage:\t\tperl sum_Row_CDT.pl\tInput_CDT_File\tOutput_TAB_File\nExample:\tperl sum_Row_CDT.pl input.cdt ouput.tab\n" unless $#ARGV == 1;
my($input, $output) = @ARGV;
open(IN, "<$input") or die "Can't open $input for reading!\n";
open(OUT, ">$output") or die "Can't open $output for reading!\n";

while(<IN>) {
	chomp;
	next if(/YORF/);
	my @temparray = split(/\t/, $_);
	$SUM = 0;
	for($x = 2; $x <= $#temparray; $x++) {
		$SUM += $temparray[$x];
	}
	print OUT $temparray[0],"\t",$SUM,"\n";
}
close IN;
close OUT;
