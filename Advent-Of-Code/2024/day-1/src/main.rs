use std::collections::HashMap;
use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;


/// Lit un fichier et retourne deux vecteurs correspondant aux colonnes.
fn read_file_to_columns(file_path: &str) -> io::Result<(Vec<i32>, Vec<i32>)> {
    let mut column1 = Vec::new();
    let mut column2 = Vec::new();

    if !Path::new(file_path).exists() {
        return Err(io::Error::new(io::ErrorKind::NotFound, "Fichier introuvable"));
    }

    let file = File::open(file_path)?;
    let reader = io::BufReader::new(file);

    for line in reader.lines() {
        let line = line?;
        let numbers: Vec<i32> = line
            .split_whitespace()
            .filter_map(|num| num.parse::<i32>().ok())
            .collect();

        if numbers.len() == 2 {
            column1.push(numbers[0]);
            column2.push(numbers[1]);
        }
    }

    Ok((column1, column2))
}

/// Trie deux vecteurs.
fn sort_columns(column1: &mut Vec<i32>, column2: &mut Vec<i32>) {
    column1.sort_unstable();
    column2.sort_unstable();
}

/// Calcule les différences absolues entre les éléments pairés de deux vecteurs.
fn calculate_distances(column1: &[i32], column2: &[i32]) -> Vec<i32> {
    column1
        .iter()
        .zip(column2.iter())
        .map(|(a, b)| (a - b).abs())
        .collect()
}

/// Calcule la somme des distances dans un vecteur.
fn sum_distances(distances: &[i32]) -> i32 {
    distances.iter().sum()
}

/// Partie 1 : Calcule la somme des distances entre les deux colonnes triées.
fn part_one_solution(column1: Vec<i32>, column2: Vec<i32>) -> i32 {
    let mut col1 = column1;
    let mut col2 = column2;

    // Trier les colonnes
    sort_columns(&mut col1, &mut col2);

    // Calculer les distances
    let distances = calculate_distances(&col1, &col2);

    // Retourner la somme des distances
    sum_distances(&distances)
}

/// Partie 2 : Calcule le score de similarité entre les deux colonnes.
fn part_two_solution(column1: Vec<i32>, column2: Vec<i32>) -> i32 {
    // Construire un HashMap pour compter les occurrences dans la seconde colonne
    let mut occurrences = HashMap::new();
    for &num in &column2 {
        *occurrences.entry(num).or_insert(0) += 1;
    }

    // Calculer le score de similarité
    column1.iter()
        .map(|&num| num * occurrences.get(&num).unwrap_or(&0))
        .sum()
}


fn main() -> io::Result<()> {
    let file_path = "input.txt";

    // Lire les colonnes depuis le fichier
    let (column1, column2) = read_file_to_columns(file_path)?;

    // Partie 1 : Somme des distances
    let distance_sum = part_one_solution(column1.clone(), column2.clone());
    println!("Partie 1 - Somme des distances : {}", distance_sum);

    // Partie 2 : Score de similarité
    let similarity_score = part_two_solution(column1, column2);
    println!("Partie 2 - Score de similarité : {}", similarity_score);

    Ok(())
}
