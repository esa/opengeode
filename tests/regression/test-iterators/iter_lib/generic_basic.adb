package body Generic_Basic is
    procedure Initialize (self: in out Basic_ASN1_Iterator) is
    begin
        --Self.Value := create;
        Self.Value.Initialize;
    end;

    function First (Item : Iterator) return Iterator_Ptr is
    begin
        Item.Ptr.Value.First;
        return Item.Ptr;
    end;

    function Next (Item : Iterator;
                   Ptr  : Iterator_Ptr) return Iterator_Ptr is
    pragma Unreferenced (Item);
    begin
        Ptr.Value.Next;
        return Ptr;
    end;

    function Iterate (self : Basic_ASN1_Iterator)
        return Forward_Iterator is
    begin
       return I: Iterator do
           I.Ptr := self'Unrestricted_Access;
       end return;
    end;
end;
