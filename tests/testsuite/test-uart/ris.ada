package ris is
    procedure Check_Queue (Result: out Boolean);
    pragma Export (C, Check_Queue, "og_check_queue");
end ris;
