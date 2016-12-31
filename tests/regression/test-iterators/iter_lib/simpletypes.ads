generic
    type Element is private;
    with function Elem_Init return Element;
    with function Has_Elem (Value: Element) return Boolean;
    with function Elem_First return Element;
    with function Elem_Next (Value: Element) return Element;
package SimpleTypes is
    type SimpleType is tagged
    record
        Value: Element;
    end record;

    procedure Initialize (Self : in out SimpleType);

    function Has_Element (Self : in out SimpleType) return Boolean is
        (Has_Elem (Self.Value));

    procedure First (Self : in out SimpleType);

    procedure Next (Self : in out SimpleType);

    function Element_Value (Self : in out SimpleType) return Element is
        (Self.Value);
end;
