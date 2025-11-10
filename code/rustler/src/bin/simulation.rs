// --- IMPORTS ---
use rustler::{entropy, get_pattern, update, Tile}; 
use std::fs;
use std::io::{self, Write}; // Import Write for flush()
use std::time::Instant;
use rayon::prelude::*;

// --- SIMULATION FOR ONE WORD ---
fn run_one_simulation(
    answer_word: &str, 
    master_answers: &Vec<String>, // The full 2331-word list
    guess_list: &Vec<String>
) -> u32 {
    
    // Correct syntax to clone the master list
    let mut current_answers: Vec<String> = master_answers.clone(); 
    let mut best_guess: String = "raise".to_string();
    let mut j = 1; // Guess count

    while j <= 6 { // Max-guess limit
        let pattern = get_pattern(&best_guess, answer_word); 

        if pattern == [Tile::Green; 5] {
            return j; // Won!
        }
        
        // Pass the *owned* Vec. 'update' (from lib.rs)
        // consumes it and returns a *new* owned Vec.
        current_answers = update(&best_guess, pattern, current_answers);

        if current_answers.len() == 1 {
            return j + 1; // Solved by deduction
        }
        if current_answers.len() == 0 {
            return 7; // Failed
        }

        // Pass a *borrow* to entropy
        best_guess = entropy(&current_answers, guess_list);
        j += 1;
    }
    
    return 7; // Failed (ran out of guesses)
}

// --- PARALLEL SIMULATION RUNNER ---
fn top1_method(runs: u32, master_answers: &Vec<String>, guess_list: &Vec<String>) -> f64 {
    
    // This is the correct parallel map/collect pattern.
    let scores: Vec<u32> = (0..runs as usize) // Iterate from 0 to 'runs'
        .into_par_iter()
        .map(|i| {
            let answer = &master_answers[i];
            
            // Pass the master list to be cloned
            println!("Running simulation number {}", i);
            run_one_simulation(answer, master_answers, guess_list)
        })
        .collect(); // Collect all the u32 scores into a Vec

    // Calculate the average score
    let total_score: u32 = scores.iter().sum();
    
    if scores.len() == 0 { return 0.0; } // Avoid division by zero
    
    total_score as f64 / scores.len() as f64
}

// --- MAIN FUNCTION ---
fn main() -> io::Result<()> {
    let answers_path = "word_list.txt";
    let guess_path = "possible_words.txt";

    // Read files into strings
    let answers_content = fs::read_to_string(answers_path)?;
    let guess_content = fs::read_to_string(guess_path)?;

    // Convert strings into Vec<String>
    let answers_vec: Vec<String> = answers_content
        .lines()
        .map(|s| s.trim().to_lowercase())
        .collect();

    let guess_vec: Vec<String> = guess_content
        .lines()
        .map(|s| s.trim().to_lowercase())
        .collect();

    // Get len from Vec, declare var
    let total_answers = answers_vec.len();
    
    print!("How many runs? (Type 'ALL' for all {} answers): ", total_answers);
    io::stdout().flush()?; // Force the prompt to show

    //  Must declare user_input as a new, empty String
    let mut user_input = String::new();
    io::stdin()
        .read_line(&mut user_input)
        .expect("failed to read line");

    // FIX: Declare 'runs' *outside* the if/else
    let mut runs: u32; // Use 'mut' so we can cap it

    // Must .trim() the newline from user_input
    if user_input.trim().to_lowercase() == "all" {
        runs = total_answers as u32;
    } else {
        // FIX: Must .trim() before parsing
        runs = user_input.trim().parse().expect("Not a number!");
        if runs > total_answers as u32 {
             println!("Warning: Runs ({}) > total answers ({}). Capping at {}.", runs, total_answers, total_answers);
             runs = total_answers as u32;
        }
    }

    println!("Running simulation for {} runs...", runs);
    let sim_start = Instant::now(); // Start timer just for simulation

    //Pass the Vecs (as references)
    let score_avg = top1_method(runs, &answers_vec, &guess_vec);

    println!("The avg score is {:.4} tries per word", score_avg);

    let duration = sim_start.elapsed();

    println!("Simulation took {:.4} seconds", duration.as_secs_f64());
    Ok(())
}
