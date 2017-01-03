package body Generic_SeqOf is

    procedure Initialize (self: in out ASN1_Variable_SeqOf) is
    begin
      self.value.length := self.length;
      if self.length >= 1 then
          self.RestVal := new P.ASN1_SeqOf(Self.Length);
          self.RestIt := new P.ASN1_SeqOf_It'(P.ASN1_SeqOf_It(Self.RestVal.Iterate));
          self.RestIt.Ptr := self.RestIt.First;
      end if;
    end;

    function Has_Element_Variable_SeqOf (Ptr: ASN1_Variable_SeqOf_Ptr)
     return Boolean is (Length_Pkg.Has_Element(Length_Pkg.Ptr(Ptr.LenIt)));

    function Iterate (self : ASN1_Variable_SeqOf)
      return Iterators_Variable_SeqOf.Forward_Iterator'Class is
    begin
     return I: ASN1_Variable_SeqOf_It do
         I.Ptr := Self'Unrestricted_Access;
     end return;
    end;

    function First (Item : ASN1_Variable_SeqOf_It) return ASN1_Variable_SeqOf_Ptr is
    begin
      -- Initialize the iterator (Compute first value)
      Item.Ptr.LenIt  := Length_Pkg.Iterator(Item.Ptr.LenVal.Iterate);

      --Item.Ptr.Value := Item.Ptr.RestIt.Ptr.Value;
      -- Copy only the actual size, since the arrays may be different in size
      Item.Ptr.Value.Data(1..Item.Ptr.RestIt.Ptr.Value.Data'Length) := Item.Ptr.RestIt.Ptr.Value.Data;
      return Item.Ptr;
    end;

    function Next (Item : ASN1_Variable_SeqOf_It;
                   Ptr  : ASN1_Variable_SeqOf_Ptr) return ASN1_Variable_SeqOf_Ptr is
        pragma Unreferenced (Item);
        Ptr_elem : Length_Pkg.Iterator_Ptr := Length_Pkg.Ptr(Ptr.LenIt);
    begin
      Ptr.RestIt.Ptr := Ptr.RestIt.Next (Ptr.RestIt.Ptr);
      if P.Has_Element_SeqOf (Ptr.RestIt.Ptr) then
          --Ptr.Value := Ptr.RestIt.Ptr.Value;
          Ptr.Value.Data(1..Ptr.RestIt.Ptr.Value.Data'Length) := Ptr.RestIt.Ptr.Value.Data;
      else
          Ptr.RestIt.Ptr := Ptr.RestIt.First;
          -- Exhausted "rest": iterate on the first item
          Ptr_elem := Ptr.LenIt.Next(Ptr_elem);
          if Length_Pkg.Has_Element (Ptr_elem) then
              Ptr.Value.Length := Integer(Ptr_elem.Value.Value);
              Ptr.Length := Ptr.Value.Length;
              Ptr.RestVal := new P.ASN1_SeqOf(Ptr.Value.Length);
              Ptr.RestIt := new P.ASN1_SeqOf_It'(P.ASN1_SeqOf_It(Ptr.RestVal.Iterate));
              Ptr.RestIt.Ptr := Ptr.RestIt.First;
              --Ptr.Value := Ptr.RestIt.Ptr.Value;
              Ptr.Value.Data(1..Ptr.RestIt.Ptr.Value.Data'Length) := Ptr.RestIt.Ptr.Value.Data;
          end if;
     end if;
     return Ptr;
    end;

end;

