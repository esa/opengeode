#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod orchestrator;
use orchestrator::*;
use orchestrator::dataview_uniqDef::*;

/// Print the current state returned by <proc>_state() (a NUL-terminated C
/// string), matching what test_ada.c / test_c.c print.
unsafe fn print_state() {
    let p = orchestrator_state();
    let s = std::ffi::CStr::from_ptr(p as *const std::os::raw::c_char);
    println!("{}", s.to_str().unwrap());
}

/// Mirrors test_ada.c: one startup, then the current state around two `other`
/// inputs.
fn main() {
    unsafe {
        println!("[C Code] Running test");

        orchestrator_startup();

        print_state();
        other();
        print_state();
        other();
        print_state();
        println!();
    }
}
