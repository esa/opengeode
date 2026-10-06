#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod complexsdl;
use complexsdl::*;
use complexsdl::dataview_uniqDef::*;

/// Print the current state returned by <proc>_state() (a NUL-terminated C
/// string), matching what the Ada and C drivers print.
unsafe fn print_state() {
    let p = complexsdl_state();
    let s = std::ffi::CStr::from_ptr(p as *const std::os::raw::c_char);
    println!("{}", s.to_str().unwrap());
}

fn main() {
    unsafe {
        complexsdl_startup();
        print_state();
        tick();
        print_state();
        tick();
        print_state();
        tick();
        print_state();
    }
}
