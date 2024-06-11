#! /usr/bin/perl

die "usage:\t\tperl determine_closest_RefPoint_output_Both.pl\tBED_File\tRef_BED_File\tUpstreamLimit\tDownstreamLimit\tOutput_File\nExample:\tperl determine_closest_RefPoint_output_Both.pl input.bed ref.bed output.bed\n" unless $#ARGV == 4;
my($input, $ref, $upstream, $downstream, $output) = @ARGV;

#chr1	9260	9261	ST3635	0	-
#chr1	31151	31152	ST0003	0	+
#chr1	33359	33360	ST0004	0	+

# Pull peaks into
open(REF, "<$ref") or die "Can't open $ref for reading!\n";
@REF_COORD = ();
while($line = <REF>) {
	chomp($line);
	@array = split(/\t/, $line);
	$MID = int(($array[1] + $array[2]) / 2);
	push(@REF_COORD, {chr => $array[0], mid => $MID, id => $array[3], dir => $array[5], line => $line});
}
close REF;
#@temp2 = sort { $$a{'start'} <=> $$b{'start'} } @temp1;
#@SORT = sort { $$a{'chr'} cmp $$b{'chr'} } @temp2;

open(IN, "<$input") or die "Can't open $input for reading!\n";
open(OUT, ">$output") or die "Can't open $output for writing!\n";
while($line = <IN>) {
	chomp($line);
	@array = split(/\t/, $line);
	$MID = int(($array[1] + $array[2]) / 2);
	$trueDIST = -99999;
	$closestIndex = -1;
	for($x = 0; $x <= $#REF_COORD; $x++) {
		if($REF_COORD[$x]{'chr'} eq $array[0]) {
			if($REF_COORD[$x]{'dir'} eq "-") { $thisDIST = $REF_COORD[$x]{'mid'} - $MID; }
			else { $thisDIST = $MID - $REF_COORD[$x]{'mid'}; }

			if($thisDIST > $upstream && $thisDIST < $downstream) {
				if($trueDIST==-99999 || abs($thisDIST) < abs($trueDIST)) {
					$trueDIST = $thisDIST;
					$closestIndex = $x;
				}
			}
		}
	}
	if($closestIndex == -1) {
		print OUT $line,"\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\n";
	} else {
		print OUT $line,"\t",$REF_COORD[$closestIndex]{'line'},"\t",$trueDIST,"\n";
	}
}
close IN;
close OUT;
