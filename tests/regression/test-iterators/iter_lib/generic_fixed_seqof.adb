with Ada.Unchecked_Conversion;

package body Generic_Fixed_SeqOf is

    procedure Initialize (self: in out ASN1_SeqOf) is
    begin
      self.value.length := self.length;
      if self.length > 1 then
          self.Rest := new ASN1_SeqOf(self.Length - 1);
          self.RestIt := new ASN1_SeqOf_It'(ASN1_SeqOf_It(self.Rest.Iterate));
          self.RestIt.Ptr := self.RestIt.First;
      end if;
    end;

    function Has_Element_SeqOf (Ptr: ASN1_SeqOf_Ptr) return Boolean is
      (P.Has_Element(P.Ptr(Ptr.FirstIt)));

    function Iterate (self : ASN1_SeqOf)
      return Iterators_SeqOf.Forward_Iterator'Class is
    begin
     return I: ASN1_SeqOf_It do
         I.Ptr := self'Unrestricted_Access;
     end return;
    end;


    function First (Item : ASN1_SeqOf_It) return ASN1_SeqOf_Ptr is
        Ptr_elem : P.Iterator_Ptr := P.Ptr(Item.Ptr.FirstIt);
    begin
      -- Initialize the iterator (Compute first value)
      Item.Ptr.FirstIt := P.Iterator(Item.Ptr.FirstVal.Iterate);
      Ptr_elem := P.First(Item.Ptr.FirstIt);
      Item.Ptr.Value.Data(1) := P.Elem_Value(Item.Ptr.FirstVal,
                                             Ptr_elem);
      if Item.Ptr.Length > 1 then
          Item.Ptr.Value.Data(2 .. Item.Ptr.Length) :=
              Item.Ptr.RestIt.Ptr.Value.Data(1..Item.Ptr.RestIt.Ptr.Length);
      end if;
      return Item.Ptr;
    end;

    function Next (Item : ASN1_SeqOf_It;
                 Ptr  : ASN1_SeqOf_Ptr) return ASN1_SeqOf_Ptr is
        pragma Unreferenced (Item);
        Ptr_elem : P.Iterator_Ptr := P.Ptr(Ptr.FirstIt);
    begin
      if Ptr.Length > 1 then
          Ptr.RestIt.Ptr := Ptr.RestIt.Next (Ptr.RestIt.Ptr);
          if Has_Element_SeqOf (Ptr.RestIt.Ptr) then
              Ptr.Value.Data (2..Ptr.Length) :=
                    Ptr.RestIt.Ptr.Value.Data (1..Ptr.RestIt.Ptr.Value.Length);
          else
              Ptr.RestIt.Ptr := Ptr.RestIt.First;
              -- Exhausted "rest": iterate on the first item
              Ptr_elem := P.Next(Ptr.FirstIt, Ptr_elem);
              if P.Has_Element (Ptr_elem) then
                  Ptr.Value.Data(1) := P.Elem_Value(Ptr.FirstVal, Ptr_elem);
                  Ptr.Value.Data(2..Ptr.Length) := Ptr.RestIt.Ptr.Value.Data (1..Ptr.RestIt.Ptr.Length);
              end if;
          end if;
     else
         -- Size is 0 or 1
         Ptr_elem := P.Next(Ptr.FirstIt, Ptr_elem);
         if P.Has_Element (Ptr_elem) then
             Ptr.Value.Data(1) := P.Elem_Value(Ptr.FirstVal, Ptr_elem);
         end if;
      end if;
     return Ptr;
    end;

end;

