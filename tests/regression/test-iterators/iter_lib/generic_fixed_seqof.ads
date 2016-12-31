with Ada.Iterator_Interfaces;

with Ada.Finalization;
use Ada.Finalization;

with generic_basic;

generic
    with package P is new Generic_Basic (<>);
package Generic_Fixed_SeqOf is

    type DataArray is array(natural range <>) of P.Element;
    type SeqOf (Max: Natural) is record
      Length : Integer;
      Data   : DataArray(1..Max);
    end record;

    type ASN1_SeqOf_Ptr;
    type ASN1_SeqOf_It;
    type ASN1_SeqOf (Size: Natural) is new Controlled
    with record
      Length   : Natural := Size;
      Value    : SeqOf (Size);
      -- First value
      FirstVal : P.Basic_ASN1_Iterator;
      FirstIt  : P.Iterator;
      -- The rest (recursive)
      Rest     : access ASN1_SeqOf;
      RestIt   : access ASN1_SeqOf_It;
    end record
      with Default_Iterator  => Iterate,
           Iterator_Element  => SeqOf,
           Constant_Indexing => Element_SeqOf_Value;

    type ASN1_SeqOf_Ptr is access all ASN1_SeqOf;

    --  Constructor (called automatically)
    procedure Initialize(self: in out ASN1_SeqOf);

    function Has_Element_SeqOf (Ptr : ASN1_SeqOf_Ptr) return Boolean;

    package Iterators_SeqOf is
      new Ada.Iterator_Interfaces (ASN1_SeqOf_Ptr, Has_Element_SeqOf);

    type ASN1_SeqOf_It is new Iterators_SeqOf.Forward_Iterator with record
      Ptr : ASN1_SeqOf_Ptr;
    end record;

    overriding function First (Item : ASN1_SeqOf_It)  return ASN1_SeqOf_Ptr;
    overriding function Next  (Item : ASN1_SeqOf_It;
                               Ptr  : ASN1_SeqOf_Ptr) return ASN1_SeqOf_Ptr;

    function Iterate (self : ASN1_SeqOf)
      return Iterators_SeqOf.Forward_Iterator'Class;

    function Element_SeqOf_Value (self : ASN1_SeqOf;
                                  Ptr  : ASN1_SeqOf_Ptr)
      return SeqOf is (self.Value);


end;
