with foo;
use foo;
with RIs;

procedure test_ada is
   B : Branches;
begin
    startup;
    
    --  First pulse using step-by-step API
    B := simu_pulse;
    while B /= Branch_End loop
       B := Execute_Transition_Step (B);
    end loop;

    --  Second pulse using step-by-step API
    B := simu_pulse;
    while B /= Branch_End loop
       B := Execute_Transition_Step (B);
    end loop;

    --  Third pulse using step-by-step API
    B := simu_pulse;
    while B /= Branch_End loop
       B := Execute_Transition_Step (B);
    end loop;
end test_ada;
