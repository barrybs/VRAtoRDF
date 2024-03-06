import re

def parse_line(line):
    """Estrae chiave e valore da una linea di testo. Ritorna None se la linea non può essere divisa correttamente."""
    parts = re.split(r'\t+', line)
    if len(parts) < 2:
        return None, None  # Ritorna None se la linea non contiene abbastanza parti
    return parts[0], parts[1]

def convert_to_rdf(input_file, output_file):
    prefixes = {
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'owl': 'http://www.w3.org/2002/07/owl#',
        'vra': 'http://purl.org/vra/',
        'so': 'http://schema.org/',
        'void': 'http://rdfs.org/ns/void#',
        'xsd': 'http://www.w3.org/2001/XMLSchema#',
        'foaf': "http://xmlns.com/foaf/0.1/"
    }
    # Definisci qui le chiavi che non richiedono le virgolette per i loro valori
    keys_without_quotes = {'rdf:type', 'rdfs:isDefinedBy', 'rdf:about', 'rdfs:subClassOf', 'owl:equivalentClass', 'rdfs:domain', 'rdfs:range'}

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:

        for prefix, uri in prefixes.items():
            outfile.write(f"@prefix {prefix}: <{uri}> .\n")
        outfile.write("\n")  # Aggiunge una riga vuota dopo i prefissi

        current_subject = None
        for line in infile:
            line = line.strip()
            if not line:  # Salta le righe vuote
                continue
            key, value = parse_line(line)
            if key is None:  # Se parse_line ritorna None, salta questa linea
                continue

            if key == 'Term Name:':  # Inizio di una nuova sezione
                if current_subject:  # Se non è il primo termine, aggiungi una riga vuota per separare i termini
                    outfile.write('.\n\n')
                current_subject = value
                outfile.write(f'{value}\n')  # Inizia la nuova sezione con il soggetto
            else:
                predicate = key.replace('rdf:', 'rdf:').replace('rdfs:', 'rdfs:').replace('owl:', 'owl:')
                for prefix, uri in prefixes.items():
                    if value.startswith(uri):
                        value = value.replace(uri, f"{prefix}:")
                        break

                if key == 'rdf:about':
                    if current_subject:  # Se non è il primo termine, aggiungi una riga vuota per separare i termini
                        outfile.write('.\n\n')
                    outfile.write(f'{value}\n')
                    current_subject = value
                else:

                    if key in keys_without_quotes:
                        outfile.write(f'    {predicate} {value} ;\n')
                    else:
                        outfile.write(f'    {predicate} "{value}" ;\n')

        # Close the last definition with a dot instead of a semicolon
        if current_subject:  # Ensure there was at least one term processed
            outfile.write('    .\n')  # Properly close the last definition

# Percorso del file di input e output
input_file = 'source_files/vra.txt'  # Sostituisci con il percorso corretto
output_file = 'turtles/vra.ttl'

convert_to_rdf(input_file, output_file)
