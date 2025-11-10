use rustler::{entropy};
use std::fs;
use std::io;
use std::time::{Instant};


fn main() -> io::Result<()> {

    let start = Instant::now();
    let answers_path = "word_list.txt"; 
    let guess_path = "possible_words.txt"; 


    let answers = fs::read_to_string(answers_path)?;
    let guess = fs::read_to_string(guess_path)?;

    // Convert the String into a Vec<String>
    let answers_vec: Vec<String> = answers
        .lines() // Split by newlines
        .map(|s| s.trim().to_lowercase()) // .strip().lower()
        .collect(); // Collect into a new Vec<String>

    let guess_vec: Vec<String> = guess
        .lines()
        .map(|s| s.trim().to_lowercase())
        .collect();

    let best_guess = entropy(&answers_vec, &guess_vec);
    
    println!("{}", best_guess);
    let duration = start.elapsed();
    println!("it took {:.4} seconds", duration.as_secs_f64());
    Ok(())
}
