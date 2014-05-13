pragma Ada_95;
with System;
package ada_main is
   pragma Warnings (Off);

   procedure adainit;
   pragma Export (C, adainit, "adainit");

   procedure adafinal;
   pragma Export (C, adafinal, "adafinal");

   type Version_32 is mod 2 ** 32;
   u00001 : constant Version_32 := 16#218f1c55#;
   pragma Export (C, u00001, "trafficlightB");
   u00002 : constant Version_32 := 16#a037fda2#;
   pragma Export (C, u00002, "trafficlightS");
   u00003 : constant Version_32 := 16#3935bd10#;
   pragma Export (C, u00003, "system__standard_libraryB");
   u00004 : constant Version_32 := 16#b31646c6#;
   pragma Export (C, u00004, "system__standard_libraryS");
   u00005 : constant Version_32 := 16#498fe5cc#;
   pragma Export (C, u00005, "adaasn1rtlB");
   u00006 : constant Version_32 := 16#a22390c3#;
   pragma Export (C, u00006, "adaasn1rtlS");
   u00007 : constant Version_32 := 16#3ffc8e18#;
   pragma Export (C, u00007, "adaS");
   u00008 : constant Version_32 := 16#129923ea#;
   pragma Export (C, u00008, "interfacesS");
   u00009 : constant Version_32 := 16#bd760655#;
   pragma Export (C, u00009, "systemS");
   u00010 : constant Version_32 := 16#0be1b996#;
   pragma Export (C, u00010, "system__exn_llfB");
   u00011 : constant Version_32 := 16#3cf218ba#;
   pragma Export (C, u00011, "system__exn_llfS");
   u00012 : constant Version_32 := 16#47eac585#;
   pragma Export (C, u00012, "system__exp_lluB");
   u00013 : constant Version_32 := 16#3da1b8a5#;
   pragma Export (C, u00013, "system__exp_lluS");
   u00014 : constant Version_32 := 16#d7975a23#;
   pragma Export (C, u00014, "system__unsigned_typesS");
   u00015 : constant Version_32 := 16#189d768f#;
   pragma Export (C, u00015, "system__fat_lfltS");
   u00016 : constant Version_32 := 16#12c24a43#;
   pragma Export (C, u00016, "ada__charactersS");
   u00017 : constant Version_32 := 16#051b1b7b#;
   pragma Export (C, u00017, "ada__characters__latin_1S");
   u00018 : constant Version_32 := 16#d7aac20c#;
   pragma Export (C, u00018, "system__ioB");
   u00019 : constant Version_32 := 16#2334f11a#;
   pragma Export (C, u00019, "system__ioS");
   u00020 : constant Version_32 := 16#47fda709#;
   pragma Export (C, u00020, "taste_basictypesB");
   u00021 : constant Version_32 := 16#ea7368bd#;
   pragma Export (C, u00021, "taste_basictypesS");
   u00022 : constant Version_32 := 16#4b642254#;
   pragma Export (C, u00022, "taste_dataviewB");
   u00023 : constant Version_32 := 16#4e7b5f72#;
   pragma Export (C, u00023, "taste_dataviewS");
   u00024 : constant Version_32 := 16#3d0b17cc#;
   pragma Export (C, u00024, "system__memoryB");
   u00025 : constant Version_32 := 16#77fdba40#;
   pragma Export (C, u00025, "system__memoryS");
   u00026 : constant Version_32 := 16#0381b3eb#;
   pragma Export (C, u00026, "ada__exceptionsB");
   u00027 : constant Version_32 := 16#813e0b0c#;
   pragma Export (C, u00027, "ada__exceptionsS");
   u00028 : constant Version_32 := 16#16173147#;
   pragma Export (C, u00028, "ada__exceptions__last_chance_handlerB");
   u00029 : constant Version_32 := 16#1f42fb5e#;
   pragma Export (C, u00029, "ada__exceptions__last_chance_handlerS");
   u00030 : constant Version_32 := 16#0071025c#;
   pragma Export (C, u00030, "system__soft_linksB");
   u00031 : constant Version_32 := 16#d02d7c88#;
   pragma Export (C, u00031, "system__soft_linksS");
   u00032 : constant Version_32 := 16#27940d94#;
   pragma Export (C, u00032, "system__parametersB");
   u00033 : constant Version_32 := 16#0b940a95#;
   pragma Export (C, u00033, "system__parametersS");
   u00034 : constant Version_32 := 16#17775d6d#;
   pragma Export (C, u00034, "system__secondary_stackB");
   u00035 : constant Version_32 := 16#a91821fb#;
   pragma Export (C, u00035, "system__secondary_stackS");
   u00036 : constant Version_32 := 16#ace32e1e#;
   pragma Export (C, u00036, "system__storage_elementsB");
   u00037 : constant Version_32 := 16#47bb7bcd#;
   pragma Export (C, u00037, "system__storage_elementsS");
   u00038 : constant Version_32 := 16#4f750b3b#;
   pragma Export (C, u00038, "system__stack_checkingB");
   u00039 : constant Version_32 := 16#1ed4ba79#;
   pragma Export (C, u00039, "system__stack_checkingS");
   u00040 : constant Version_32 := 16#7b9f0bae#;
   pragma Export (C, u00040, "system__exception_tableB");
   u00041 : constant Version_32 := 16#2c18daf0#;
   pragma Export (C, u00041, "system__exception_tableS");
   u00042 : constant Version_32 := 16#5665ab64#;
   pragma Export (C, u00042, "system__htableB");
   u00043 : constant Version_32 := 16#3ede485b#;
   pragma Export (C, u00043, "system__htableS");
   u00044 : constant Version_32 := 16#8b7dad61#;
   pragma Export (C, u00044, "system__string_hashB");
   u00045 : constant Version_32 := 16#9beadec1#;
   pragma Export (C, u00045, "system__string_hashS");
   u00046 : constant Version_32 := 16#aad75561#;
   pragma Export (C, u00046, "system__exceptionsB");
   u00047 : constant Version_32 := 16#b188cee2#;
   pragma Export (C, u00047, "system__exceptionsS");
   u00048 : constant Version_32 := 16#010db1dc#;
   pragma Export (C, u00048, "system__exceptions_debugB");
   u00049 : constant Version_32 := 16#85062381#;
   pragma Export (C, u00049, "system__exceptions_debugS");
   u00050 : constant Version_32 := 16#b012ff50#;
   pragma Export (C, u00050, "system__img_intB");
   u00051 : constant Version_32 := 16#bfade697#;
   pragma Export (C, u00051, "system__img_intS");
   u00052 : constant Version_32 := 16#dc8e33ed#;
   pragma Export (C, u00052, "system__tracebackB");
   u00053 : constant Version_32 := 16#dcf1d220#;
   pragma Export (C, u00053, "system__tracebackS");
   u00054 : constant Version_32 := 16#907d882f#;
   pragma Export (C, u00054, "system__wch_conB");
   u00055 : constant Version_32 := 16#029d2868#;
   pragma Export (C, u00055, "system__wch_conS");
   u00056 : constant Version_32 := 16#22fed88a#;
   pragma Export (C, u00056, "system__wch_stwB");
   u00057 : constant Version_32 := 16#2f8c0469#;
   pragma Export (C, u00057, "system__wch_stwS");
   u00058 : constant Version_32 := 16#b8a9e30d#;
   pragma Export (C, u00058, "system__wch_cnvB");
   u00059 : constant Version_32 := 16#1c63aebe#;
   pragma Export (C, u00059, "system__wch_cnvS");
   u00060 : constant Version_32 := 16#75729fba#;
   pragma Export (C, u00060, "system__wch_jisB");
   u00061 : constant Version_32 := 16#481135aa#;
   pragma Export (C, u00061, "system__wch_jisS");
   u00062 : constant Version_32 := 16#ada34a87#;
   pragma Export (C, u00062, "system__traceback_entriesB");
   u00063 : constant Version_32 := 16#ef57e814#;
   pragma Export (C, u00063, "system__traceback_entriesS");
   u00064 : constant Version_32 := 16#1530815b#;
   pragma Export (C, u00064, "system__crtlS");
   --  BEGIN ELABORATION ORDER
   --  ada%s
   --  ada.characters%s
   --  ada.characters.latin_1%s
   --  interfaces%s
   --  system%s
   --  system.exn_llf%s
   --  system.exn_llf%b
   --  system.htable%s
   --  system.img_int%s
   --  system.img_int%b
   --  system.io%s
   --  system.io%b
   --  system.parameters%s
   --  system.parameters%b
   --  system.crtl%s
   --  system.standard_library%s
   --  system.exceptions_debug%s
   --  system.exceptions_debug%b
   --  system.storage_elements%s
   --  system.storage_elements%b
   --  system.stack_checking%s
   --  system.stack_checking%b
   --  system.string_hash%s
   --  system.string_hash%b
   --  system.htable%b
   --  system.traceback_entries%s
   --  system.traceback_entries%b
   --  ada.exceptions%s
   --  system.soft_links%s
   --  system.unsigned_types%s
   --  system.exp_llu%s
   --  system.exp_llu%b
   --  system.fat_lflt%s
   --  system.wch_con%s
   --  system.wch_con%b
   --  system.wch_cnv%s
   --  system.wch_jis%s
   --  system.wch_jis%b
   --  system.wch_cnv%b
   --  system.wch_stw%s
   --  system.wch_stw%b
   --  ada.exceptions.last_chance_handler%s
   --  ada.exceptions.last_chance_handler%b
   --  system.exception_table%s
   --  system.exception_table%b
   --  system.exceptions%s
   --  system.exceptions%b
   --  system.memory%s
   --  system.memory%b
   --  system.standard_library%b
   --  system.secondary_stack%s
   --  system.soft_links%b
   --  system.secondary_stack%b
   --  system.traceback%s
   --  ada.exceptions%b
   --  system.traceback%b
   --  adaasn1rtl%s
   --  adaasn1rtl%b
   --  taste_basictypes%s
   --  taste_basictypes%b
   --  taste_dataview%s
   --  taste_dataview%b
   --  trafficlight%s
   --  trafficlight%b
   --  END ELABORATION ORDER


end ada_main;
