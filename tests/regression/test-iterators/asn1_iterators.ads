--  This file was generated automatically by TASTE: DO NOT EDIT

--  Generic constructs for common/basic types
with generic_integer;
with generic_seqof;

package ASN1_Iterators is

    --  ASN.1 File /home/mperroti/taste/opengeode/tests/regression/test-iterators/dataview-uniq.asn
    --  Module name: TASTE-BasicTypes

    --  List of exported types: "T-Int", "T-SeqOf"

    --  Imported modules  --
    --  End imported modules --

    --  Type "T-Int defined at line 4
    package T_Int_pkg is new Generic_Integer (Min => 0, Max => 4);

    --  Type "T-SeqOf defined at line 6
    package T_SeqOf_pkg is new Generic_SeqOf (Min => 1, Max => 4, Basic => T_Int_Pkg.It);



end;