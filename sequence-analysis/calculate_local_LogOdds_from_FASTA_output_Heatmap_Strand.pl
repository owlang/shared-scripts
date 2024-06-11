#! /usr/bin/perl/

die "FASTA_File\tMotif_File\tOutput_Forward\tOutput_Reverse\n" unless $#ARGV == 3;
my($input, $motif, $outF, $outR) = @ARGV;

open(MOT, "<$motif") or die "Can't open $motif for reading!\n";
my @PWM;
while(<MOT>){
        chomp;
        my @tmp = split(/\t/, $_);
        push(@PWM, [@tmp]);
}
close MOT;

open(IN, "<$input") or die "Can't open $input for reading!\n";
open(OUTF, ">$outF") or die "Can't open $outF for writing!\n";
open(OUTR, ">$outR") or die "Can't open $outR for writing!\n";

$counter = 0;
$currentID = "";
$line = "";
while($line = <IN>) {
	chomp($line);
	if($line =~ ">") {
		$currentID = substr $line, 1;
	} else {
		$line = uc $line;
	        $rcline = reverse $line;
        	$rcline =~ tr/ACGTacgt/TGCAtgca/;
	        @array = split(//, $line);

		$A = $T = $G = $C = 0;
		for($x = 0; $x <= $#array; $x++) {
			if($array[$x] eq "A") { $A++; }
			elsif($array[$x] eq "T") { $T++; }
			elsif($array[$x] eq "G") { $G++; }
			elsif($array[$x] eq "C") { $C++; }
		}
		$pAT = $pGC = 0;
		if($A + $T + $G + $C != 0) {
			$pAT = ($A + $T) / (2 * ($A + $T + $G + $C));
			$pGC = ($G + $C) / (2 * ($A + $T + $G + $C));
		}
		if($pAT != 0 && $pGC != 0) {
			@localPWM = ();
			for($x = 1; $x <= $#PWM; $x++) {
				@tmp = ();
				push(@tmp, $PWM[$x][0] + $pAT);
				push(@tmp, $PWM[$x][1] + $pGC);
				push(@tmp, $PWM[$x][2] + $pGC);
				push(@tmp, $PWM[$x][3] + $pAT);
				$SUM = 0;
				for($y = 0; $y <= $#tmp; $y++) {
					$SUM += $tmp[$y];
				}
				$tmp[0] = log(($tmp[0]/$SUM) / $pAT) / log(2);
				$tmp[1] = log(($tmp[1]/$SUM) / $pGC) / log(2);
				$tmp[2] = log(($tmp[2]/$SUM) / $pGC) / log(2);
				$tmp[3] = log(($tmp[3]/$SUM) / $pAT) / log(2);
				push(@localPWM, [@tmp]);
			}

			if($counter == 0) {
				print OUTF "YORF\tNAME";
				print OUTR "YORF\tNAME";
				for($x = 0; $x <= $#array - $#localPWM; $x++) {
	                                print OUTF "\t$x";
					print OUTR "\t$x";
				}
				print OUTF "\n";
				print OUTR "\n";
			}
			@SCOREarray = ();
                        @RCSCOREarray = ();
			for($x = 0; $x <= $#array - $#localPWM; $x++) {
				$SCORE = 0;
				$RCSCORE = 0;
				@SEQ = split(//, substr $line, $x, $#localPWM + 1);
				@RCSEQ = split(//, substr $rcline, $x, $#localPWM + 1);
				for($i = 0; $i <= $#SEQ; $i++) {
					if($SEQ[$i] eq "A") { $SCORE += $localPWM[$i][0]; }
					elsif($SEQ[$i] eq "C") { $SCORE += $localPWM[$i][1]; } 
					elsif($SEQ[$i] eq "G") { $SCORE += $localPWM[$i][2]; } 
					elsif($SEQ[$i] eq "T") { $SCORE += $localPWM[$i][3]; } 
					
					if($RCSEQ[$i] eq "A") { $RCSCORE += $localPWM[$i][0]; }
	                                elsif($RCSEQ[$i] eq "C") { $RCSCORE += $localPWM[$i][1]; } 
	                                elsif($RCSEQ[$i] eq "G") { $RCSCORE += $localPWM[$i][2]; } 
	                                elsif($RCSEQ[$i] eq "T") { $RCSCORE += $localPWM[$i][3]; } 
				}
				push(@SCOREarray, $SCORE);
				push(@RCSCOREarray, $RCSCORE);
				
			}
			print OUTF "$currentID\t$currentID";
			print OUTR "$currentID\t$currentID";
			for($x = 0; $x <= $#SCOREarray; $x++) {
				print OUTF "\t$SCOREarray[$x]";
				print OUTR "\t$RCSCOREarray[$#RCSCOREarray - $x]";
			}
			print OUTF "\n";
			print OUTR "\n";
			$counter++;
		}
	}
}

close IN;
close OUTF;
close OUTR;
