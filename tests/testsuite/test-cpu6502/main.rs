#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod cpu_6502;
use cpu_6502::*;
use cpu_6502::dataview_uniqDef::*;

fn main() {
    unsafe {
        cpu_6502_startup();
    }
}
