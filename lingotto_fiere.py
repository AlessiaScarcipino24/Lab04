import csv

class Stand:
    # classe per rappresentare uno stand generico
    def __init__(self, codice, superficie, padiglione, prezzoBase):
        self.codice = codice
        self.superficie = superficie
        self.padiglione = padiglione
        self.prezzoBase = float(prezzoBase)
        self.espositore = None # riferimento all'espositore assegnato

    def calcolaPrezzo(self):
        # restituisce il prezzo finale dello stand (per questo modello corrisponde al prezzo base)
        return float(self.prezzoBase)

    def __lt__(self, other):
        # confronto tra stand per l'ordinamento
        return self.calcolaPrezzo() < other.calcolaPrezzo()

    def __str__(self):
        if self.espositore is None:
            stato = 'Disponibile'
        else:
            stato = f'Occupato da {self.espositore.codice}'
        return f'{self.codice}: Standard | {self.superficie} mq - Padiglione {self.padiglione} - Prezzo: {self.calcolaPrezzo():.2f} euro - {stato}'


class StandPreseElettriche(Stand):
    # sottoclasse di Stand per gli stand dotati di prese elettriche aggiuntive
    def __init__(self, codice, superficie, padiglione, prezzoBase, numeroPrese):
        super().__init__(codice, superficie, padiglione, prezzoBase)
        self.numeroPrese = int(numeroPrese)

    def calcolaPrezzo(self):
        # sovrascrive il calcolo del prezzo applicando il sovrapprezzo del 7% per ogni presa extra
        return float(self.prezzoBase * (1 + 0.07 * self.numeroPrese))

    def __str__(self):
        if self.espositore is None:
            stato = 'Disponibile'
        else:
            stato = f'Occupato da {self.espositore.codice}'
        return f'{self.codice}: Prese Extra | {self.superficie} mq - Padiglione {self.padiglione} - Prezzo: {self.calcolaPrezzo():.2f} euro - Prese aggiuntive: {self.numeroPrese} - {stato}'


class StandPremium(Stand):
    # sottoclasse di Stand per gli stand di tipo Premium con posizione specifica
    def __init__(self, codice, superficie, padiglione, prezzoBase, posizione):
        super().__init__(codice, superficie, padiglione, prezzoBase)
        self.posizione = posizione

    def calcolaPrezzo(self):
        # sovrascrive il calcolo del prezzo applicando un sovrapprezzo fisso del 30%
        return float(self.prezzoBase * 1.30)

    def __str__(self):
        if self.espositore is None:
            stato = 'Disponibile'
        else:
            stato = f'Occupato da {self.espositore.codice}'
        return f'{self.codice}: Premium ({self.posizione}) | {self.superficie} mq - Padiglione {self.padiglione} - Prezzo: {self.calcolaPrezzo():.2f} euro - {stato}'


class Espositore:
    # classe per rappresentare un espositore registrato
    def __init__(self, codice, nome, cognome):
        self.codice = codice
        self.nome = nome
        self.cognome = cognome
        self.stand = None # riferimento allo stand assegnato

    def __str__(self):
        if self.stand:
            str_stand = f'Stand: {self.stand.codice}'
        else:
            str_stand = 'Nessuno stand assegnato'
        return f'Espositore [{self.codice}] {self.nome} {self.cognome} - {str_stand}'


class LingottoFiere:
    def __init__(self, nome):
        """Inizializza gli attributi e le strutture dati"""
        self.__nome = nome
        self.stand = {} # dizionario {codiceStand: oggettoStand}
        self.espositori = {} # dizionario {codiceEspositore: oggettoEspositore}

    """Aggiungere setter e getter se necessari"""
    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, nuovo_nome):
        self.__nome = nuovo_nome


    def carica_file_dati(self, file_path):
        """Carica i dati (stand ed espositori) dal file"""
        stand = []
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                reader = csv.DictReader(f, fieldnames=['C1','C2','C3','C4','C5'])

                for row in reader:
                    codice = row['C1']

                    #distinguiamo se la riga appartiene a uno stand o a un espositore in base al prefisso
                    codice = codice.strip()
                    if codice.startswith('ST'):
                        superficie = int(row['C2'].strip())
                        padiglione = int(row['C3'].strip())
                        prezzoBase = float(row['C4'].strip())

                        # tipologie di stand
                        if not row['C5'] or row['C5'].strip() == '':
                            oggettoStand = Stand(codice, superficie, padiglione, prezzoBase)
                        else:
                            valoreExtra = row['C5'].strip()
                            if valoreExtra.isdigit():
                                oggettoStand = StandPreseElettriche(codice, superficie, padiglione, prezzoBase, int(valoreExtra))
                            else:
                                oggettoStand = StandPremium(codice, superficie, padiglione, prezzoBase, valoreExtra)

                        self.stand[codice] = oggettoStand

                    elif codice.startswith('ES'):
                        nome = row['C2'].strip()
                        cognome = row['C3'].strip()
                        oggettoEspositore = Espositore(codice, nome, cognome)
                        self.espositori[codice] = oggettoEspositore

        except FileNotFoundError:
            print('Impossibile trovare il file')
            return None


    def assegna_stand_a_espositore(self, codice_stand, codice_espositore):
        """Associa uno stand a un espositore"""
        if codice_stand not in self.stand: # verifica che lo stand esista
            print(f"Errore: lo stand '{codice_stand}' non esiste nel sistema")
            return False

        if codice_espositore not in self.espositori: # verifica che l'espositore esista
            print(f"Errore: l'espositore '{codice_espositore}' non esiste nel sistema")
            return False

        s = self.stand[codice_stand]
        e = self.espositori[codice_espositore]

        if s.espositore is not None: # verifica che lo stand sia disponibile
            print(f'Errore: Lo stand {codice_stand} è già occupato.')
            return False

        if e.stand is not None: # verifica che l'espositore non abbia già uno stand
            print(f"Errore: L'espositore {codice_espositore} possiede già uno stand.")
            return False

        # se tutti i controlli sono superati, effettuiamo l'assegnazione bidirezionale
        s.espositore = e
        e.stand = s

        print('Stand assegnato con successo!')
        return True


    def elenca_espositori(self):
        """Stampa l'elenco degli espositori mostrando, per ognuno, lo stand a cui è associato, quando applicabile """
        if not self.espositori:
            print('Nessun espositore registrato.')
            return
        for e in self.espositori.values():
            print(e)


    def stand_ordinati_per_prezzo(self):
        """Restituisce la lista ordinata degli stand in base al prezzo"""
        return sorted(list(self.stand.values()))