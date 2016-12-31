package body SimpleTypes is
    procedure Initialize (Self : in out SimpleType) is
    begin
        Self.Value := Elem_Init;
    end;

    procedure First (Self : in out SimpleType) is
    begin
        Self.Value := Elem_First;
    end;

    procedure Next (Self : in out SimpleType) is
    begin
        Self.Value := Elem_Next (Self.Value);
    end;
end;
