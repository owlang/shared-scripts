#! /usr/bin/perl/

die "usage:\t\tperl shift_BED_center.pl\tBED_File\tShift(bp) [- = upstream, + = downstream]\tOutput_File\n" unless $#ARGV == 2;
my($input, $SHIFT, $output) = @ARGV;
open(IN, "<$input") or die "Can't open $input for reading!\n";
open(OUT, ">$output") or die "Can't open $output for reading!\n";

#chr1	202432145	202432225	chr1_202432185	150	+
#chr15	48645697	48645777	chr15_48645737	95	+
#chr10	14227415	14227495	chr10_14227455	90	+
#chr2	133030544	133030624	chr2_133030584	71	+

@COORD = ();
while($line = <IN>) {
	chomp($line);
        if((substr $line, 0, 1) eq "#") {
                print OUT $line,"\n";
        } else {
		my @array = split(/\t/, $line);
		$MID = int(($array[1] + $array[2]) / 2);
		#print $array[5],"\n";
		if($array[5] =~ "-") { $MID -= $SHIFT; }
		else { $MID += $SHIFT; }
		$newStop = $MID + 1;
		print OUT "$array[0]\t$MID\t$newStop";
		for($x = 3; $x <= $#array; $x++) {
			print OUT "\t$array[$x]";
		}
		print OUT "\n";
	}
}
close IN;
close OUT;
