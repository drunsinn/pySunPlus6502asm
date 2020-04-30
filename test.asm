ADC #01D
ADC #01010101B
ADC #FFH
this_is_a_label:
ADC #%00000001
ADC $#0030H ;this is a comment with spaces
ADC $#0500H,X
ADC $#28D
      ADC $#60D,X
ADC ($#20H,X)
only_a_label:
;ADC ($#31FEH) ;(this_comment_uses%specital!characters!)
label_with_instr: ADC ($#20D),Y
ADC $#30D
;ASL #01D
ASL $#01D
include abc.asm
AND #255D
AND $#01D
ADC this_is_a_label
AND $#01D
AND $#01D
ASL A
CLC
CLD
CLI
