pragma Ada_95;
pragma Source_File_Name (ada_main, Spec_File_Name => "b~trafficlight.ads");
pragma Source_File_Name (ada_main, Body_File_Name => "b~trafficlight.adb");

package body ada_main is
   pragma Warnings (Off);

   E31 : Short_Integer; pragma Import (Ada, E31, "system__soft_links_E");
   E15 : Short_Integer; pragma Import (Ada, E15, "system__fat_lflt_E");
   E41 : Short_Integer; pragma Import (Ada, E41, "system__exception_table_E");
   E47 : Short_Integer; pragma Import (Ada, E47, "system__exceptions_E");
   E35 : Short_Integer; pragma Import (Ada, E35, "system__secondary_stack_E");
   E06 : Short_Integer; pragma Import (Ada, E06, "adaasn1rtl_E");
   E21 : Short_Integer; pragma Import (Ada, E21, "taste_basictypes_E");
   E23 : Short_Integer; pragma Import (Ada, E23, "taste_dataview_E");
   E02 : Short_Integer; pragma Import (Ada, E02, "trafficlight_E");

   Local_Priority_Specific_Dispatching : constant String := "";
   Local_Interrupt_States : constant String := "";

   Is_Elaborated : Boolean := False;

   procedure adafinal is
   begin
      if not Is_Elaborated then
         return;
      end if;
      Is_Elaborated := False;
      null;
   end adafinal;

   type No_Param_Proc is access procedure;

   procedure adainit is
      Main_Priority : Integer;
      pragma Import (C, Main_Priority, "__gl_main_priority");
      Time_Slice_Value : Integer;
      pragma Import (C, Time_Slice_Value, "__gl_time_slice_val");
      WC_Encoding : Character;
      pragma Import (C, WC_Encoding, "__gl_wc_encoding");
      Locking_Policy : Character;
      pragma Import (C, Locking_Policy, "__gl_locking_policy");
      Queuing_Policy : Character;
      pragma Import (C, Queuing_Policy, "__gl_queuing_policy");
      Task_Dispatching_Policy : Character;
      pragma Import (C, Task_Dispatching_Policy, "__gl_task_dispatching_policy");
      Priority_Specific_Dispatching : System.Address;
      pragma Import (C, Priority_Specific_Dispatching, "__gl_priority_specific_dispatching");
      Num_Specific_Dispatching : Integer;
      pragma Import (C, Num_Specific_Dispatching, "__gl_num_specific_dispatching");
      Main_CPU : Integer;
      pragma Import (C, Main_CPU, "__gl_main_cpu");
      Interrupt_States : System.Address;
      pragma Import (C, Interrupt_States, "__gl_interrupt_states");
      Num_Interrupt_States : Integer;
      pragma Import (C, Num_Interrupt_States, "__gl_num_interrupt_states");
      Unreserve_All_Interrupts : Integer;
      pragma Import (C, Unreserve_All_Interrupts, "__gl_unreserve_all_interrupts");
      Detect_Blocking : Integer;
      pragma Import (C, Detect_Blocking, "__gl_detect_blocking");
      Default_Stack_Size : Integer;
      pragma Import (C, Default_Stack_Size, "__gl_default_stack_size");
      Leap_Seconds_Support : Integer;
      pragma Import (C, Leap_Seconds_Support, "__gl_leap_seconds_support");

      procedure Install_Handler;
      pragma Import (C, Install_Handler, "__gnat_install_handler");

      Handler_Installed : Integer;
      pragma Import (C, Handler_Installed, "__gnat_handler_installed");

      Finalize_Library_Objects : No_Param_Proc;
      pragma Import (C, Finalize_Library_Objects, "__gnat_finalize_library_objects");
   begin
      if Is_Elaborated then
         return;
      end if;
      Is_Elaborated := True;
      Main_Priority := -1;
      Time_Slice_Value := -1;
      WC_Encoding := 'b';
      Locking_Policy := ' ';
      Queuing_Policy := ' ';
      Task_Dispatching_Policy := ' ';
      Priority_Specific_Dispatching :=
        Local_Priority_Specific_Dispatching'Address;
      Num_Specific_Dispatching := 0;
      Main_CPU := -1;
      Interrupt_States := Local_Interrupt_States'Address;
      Num_Interrupt_States := 0;
      Unreserve_All_Interrupts := 0;
      Detect_Blocking := 0;
      Default_Stack_Size := -1;
      Leap_Seconds_Support := 0;

      if Handler_Installed = 0 then
         Install_Handler;
      end if;

      if E31 = 0 then
         System.Soft_Links'Elab_Spec;
      end if;
      if E15 = 0 then
         System.Fat_Lflt'Elab_Spec;
      end if;
      E15 := E15 + 1;
      if E41 = 0 then
         System.Exception_Table'Elab_Body;
      end if;
      E41 := E41 + 1;
      if E47 = 0 then
         System.Exceptions'Elab_Spec;
      end if;
      E47 := E47 + 1;
      if E31 = 0 then
         System.Soft_Links'Elab_Body;
      end if;
      E31 := E31 + 1;
      if E35 = 0 then
         System.Secondary_Stack'Elab_Body;
      end if;
      E35 := E35 + 1;
      E06 := E06 + 1;
      E21 := E21 + 1;
      E23 := E23 + 1;
      if E02 = 0 then
         trafficlight'elab_body;
      end if;
      E02 := E02 + 1;
   end adainit;

--  BEGIN Object file/option list
   --   ./adaasn1rtl.o
   --   ./taste_basictypes.o
   --   ./taste_dataview.o
   --   ./trafficlight.o
   --   -L./
   --   -L/usr/lib/gcc/i486-linux-gnu/4.8/adalib/
   --   -shared
   --   -lgnat-4.8
--  END Object file/option list   

end ada_main;
