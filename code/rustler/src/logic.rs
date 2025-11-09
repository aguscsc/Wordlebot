use rayon::prelude::*;
use std::collections::HashMap;


#[derive(Debug, PartialEq, Eq, Hash, Clone, Copy)]
pub enum Tile {
    Grey,
    Yellow,
    Green,
}

pub fn get_pattern(guess: &str, answer: &str) -> [Tile; 5] {
    
    let mut pattern = [Tile::Grey; 5];
    
    // Initialize the list as Vec<Option<char>>
    // This lets us use 'None' to mark "used" letters
    // .map(Some) turns 'a' into Some('a')
    let mut answer_chars: Vec<Option<char>> = answer.chars().map(Some).collect();

    
    // --- Find Greens ---
    for (i, guess_char) in guess.chars().enumerate() {
        
        // Check if the 'Some(char)' matches the one in our list
        if answer_chars[i] == Some(guess_char) {
            pattern[i] = Tile::Green;
            answer_chars[i] = None; 
        }
    }

    // --- Find Yellows ---
    for (i, guess_char) in guess.chars().enumerate() {
        
        if pattern[i] == Tile::Green {
            continue;
        }

        if let Some(answer_char_opt) = answer_chars.iter_mut().find(|opt| **opt == Some(guess_char)) {
            pattern[i] = Tile::Yellow;
            *answer_char_opt = None; // "Use it up" by setting its box to None
        }
    }

    return pattern;
}


pub fn entropy(answers: &Vec<String>, guess: &Vec<String>) -> String {
    
    if answers.len() <= 2 {
        println!("Only {} answer(s) left. Guessing: {}", answers.len(), answers[0]);
        return answers[0].clone();
    }

    let current_answers_count = answers.len() as f64;

    // Create the default String here.
    // It will "live" for the entire function.
    let default_guess = "none".to_string();

    //  We use Rayon to find the (word, score) tuple
    let best_guess_tuple = guess
        .par_iter()  // <-- This makes the loop parallel
        .map(|guess_word| {
            // It now runs in parallel for each guess_word.
            let mut patterns_group: HashMap<[Tile; 5], u32> = HashMap::with_capacity(238);

            for answer in answers {
                let pattern = get_pattern(guess_word, answer);
                *patterns_group.entry(pattern).or_insert(0) += 1;
            }

            let mut entropy: f64 = 0.0;
            for group_size in patterns_group.values() {
                let p = (*group_size as f64) / current_answers_count;
                if p > 0.0 {
                    entropy += p * (-p.log2());
                }
            }
            // --- End of loop code ---
            
            // Return the (word, score) tuple
            (guess_word, entropy)
        })
        // Find the tuple with the highest entropy
        .reduce(|| (&default_guess, -1.0), // A default value
            |a, b| if a.1 > b.1 { a } else { b } // The comparison
        );

    println!(
        "the best guess is {}, giving {:.4} bits of information",
        best_guess_tuple.0, best_guess_tuple.1
    );

    // Convert the final &String to an owned String
    best_guess_tuple.0.to_string()
}

