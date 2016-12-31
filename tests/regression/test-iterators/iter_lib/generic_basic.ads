with Ada.Iterator_Interfaces;
with Ada.Finalization;
use Ada.Finalization;
with SimpleTypes;

generic
    with package P is new SimpleTypes (<>);
package Generic_Basic is
    -- Provides an iterator for a basic type
    subtype Element is P.Element;

    type Basic_ASN1_Iterator is new Controlled
    with record
        Value : P.SimpleType;
    end record
        with Default_Iterator  => Iterate,
             Iterator_Element  => P.Element,
             Constant_Indexing => Elem_Value;

    procedure Initialize(self: in out Basic_ASN1_Iterator);

    type Iterator_Ptr is access all Basic_ASN1_Iterator;

    function Has_Element (Ptr : Iterator_Ptr) return Boolean is
        (Ptr.Value.Has_Element);

    package Iterators is
        new Ada.Iterator_Interfaces (Iterator_Ptr, Has_Element);

    type Iterator is new Iterators.Forward_Iterator with record
        Ptr : Iterator_Ptr;
    end record;

    function Ptr (Item: Iterator) return Iterator_Ptr is (Item.Ptr);

    overriding function First (Item : Iterator)     return Iterator_Ptr;
    overriding function Next  (Item : Iterator;
                               Ptr  : Iterator_Ptr) return Iterator_Ptr;

    subtype Forward_Iterator is Iterators.Forward_Iterator'Class;

    function Iterate (self : Basic_ASN1_Iterator) return Forward_Iterator;

    function Elem_Value (self : Basic_ASN1_Iterator;
                         Ptr  : Iterator_Ptr)
    return P.Element is (Ptr.Value.Element_Value);
end;
