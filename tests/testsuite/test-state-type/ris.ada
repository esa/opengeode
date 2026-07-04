package ris is
    procedure Check_Queue (Result: out Boolean);
    pragma Export (C, Check_Queue, "foo_check_queue");
end ris;
