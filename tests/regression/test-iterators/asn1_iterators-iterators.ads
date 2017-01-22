--  This file was generated automatically by TASTE: DO NOT EDIT

--  Generic constructs for common/basic types
with generic_integer;
with generic_seqof;
with asn1_iterators;
pragma Unreferenced (asn1_iterators);
with Interfaces;
use Interfaces;
with Ada.Strings.Unbounded;

package ASN1_Iterators.iterators is
    package Str renames Ada.Strings.Unbounded;
    use Str;

    --  ASN.1 File dataview-uniq.asn
    --  Module TASTE_BasicTypes
    --  List of exported types: "T-Int", "T-SeqOf"

    --  Imported modules: 
    --  End imported modules --

    --  Type "T-Int defined at line 4
    package T_Int_pkg is
        subtype ASN1_Type is asn1SccT_Int;
        package Inner is new Generic_Integer (Min => 0, Max => 4);
        package It renames Inner.It;
        procedure To_ASN1(from: Interfaces.Integer_64; to: out ASN1_Type);
        subtype Instance is Inner.Instance;
        function Image(Elm: ASN1_Type) return String;
    end;
    --  Type "T-SeqOf defined at line 6
    package T_SeqOf_pkg is
        subtype ASN1_Type is asn1SccT_SeqOf;
        package Inner is new Generic_SeqOf (Min => 1, Max => 4, Basic => T_Int_Pkg.It);
        use T_Int_Pkg;
        procedure To_ASN1(from: Inner.MySeqOf; to: out ASN1_Type);
        subtype Instance is Inner.Instance;
        function Image(Elm: ASN1_Type) return String;
    end;

end;