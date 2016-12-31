with Ada.Iterator_Interfaces;

with Ada.Finalization;
use Ada.Finalization;

with generic_fixed_seqof;
with generic_integer;
with generic_basic;

-- Iterator for a variable-size array of basic type
generic
    Min : Integer;
    Max : Integer;
    with package Basic is new Generic_Basic (<>);
package Generic_SeqOf is

    Package P is new Generic_Fixed_SeqOF (P => Basic);
    -- Create an integer type with a range constraint to iterate on
    package Length_ty is new Generic_Integer (Min, Max);
    -- Instantiate the package to iterate on the integer for the length
    package Length_Pkg renames Length_ty.It;

    type ASN1_Variable_SeqOf_Ptr is private;
    subtype MySeqOf is P.SeqOf(Max);
    type ASN1_Variable_SeqOf is new Controlled
    with record
        Length   : Natural := Min;
        Value    : MySeqOf; -- P.SeqOf(Max);
        -- Iterate on the length
        LenVal   : Length_ty.Instance;
        LenIt    : Length_Pkg.Iterator;
        -- And on the value
        RestVal  : access P.ASN1_SeqOf;
        RestIt   : access P.ASN1_SeqOf_It;
    end record
        with Default_Iterator  => Iterate,
             Iterator_Element  => MySeqOf, --P.SeqOf,
             Constant_Indexing => Element_Variable_SeqOf_Value;

    --  Constructor (called automatically)
    procedure Initialize(self: in out ASN1_Variable_SeqOf);

    function Has_Element_Variable_SeqOf (Ptr : ASN1_Variable_SeqOf_Ptr)
     return Boolean;

    package Iterators_Variable_SeqOf is
     new Ada.Iterator_Interfaces (ASN1_Variable_SeqOf_Ptr,
                                  Has_Element_Variable_SeqOf);

    type ASN1_Variable_SeqOf_It
     is new Iterators_Variable_SeqOf.Forward_Iterator with record
        Ptr : ASN1_Variable_SeqOf_Ptr;
    end record;

    overriding
    function First (Item : ASN1_Variable_SeqOf_It)
     return ASN1_Variable_SeqOf_Ptr;

    overriding
    function Next  (Item : ASN1_Variable_SeqOf_It;
                    Ptr  : ASN1_Variable_SeqOf_Ptr)
     return ASN1_Variable_SeqOf_Ptr;

    function Iterate (self : ASN1_Variable_SeqOf)
     return Iterators_Variable_SeqOf.Forward_Iterator'Class;

    function Element_Variable_SeqOf_Value (Self : ASN1_Variable_SeqOf;
                                           Ptr  : ASN1_Variable_SeqOf_Ptr)
     --return P.SeqOf is (Self.Value);
     return MySeqOf is (Self.Value);

    subtype Instance is ASN1_Variable_SeqOf;

    private
    type ASN1_Variable_SeqOf_Ptr is access all ASN1_Variable_SeqOf;

end;

