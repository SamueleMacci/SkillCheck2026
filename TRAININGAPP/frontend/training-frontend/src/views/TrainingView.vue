<template>
  <div>
    <div class="navbar">
      <router-link to="/">Home</router-link>
      <router-link to="/upload">Carica Curriculum</router-link>
    </div>

    <div class="training-container">
      <div class="main-content" @mousedown="startSelection" @mouseup="endSelection">
        <!-- Mini riquadro per visualizzare PDF -->
        <div class="mini-pdf-box" @click="openPdf">
          Visualizza PDF
        </div>

        <button @click="openEditor" class="edit-button" style="margin-left: 10px;">
          Modifica il testo del curriculum
        </button>


        <!-- Pulsante Salva -->
        <button v-if="hasChanges" @click="saveText" class="save-button" style="margin-left: 10px;">
          Salva le modifiche
        </button>

        <!-- Modale PDF in sovrimpressione -->
        <div v-if="showFullPdf" class="pdf-modal" @click.self="closePdf">
          <embed :src="pdfUrl" type="application/pdf" width="80%" height="600px" />
        </div>

        <!--Testo curriculum-->
        <h1>CURRICULUM</h1>
        <div @mousedown="startSelection" @mouseup="endSelection">
          <div v-for="(paragraph, pIndex) in paragraphs" :key="pIndex">
            <p class="curriculum-paragraph">
              <span v-for="(word, index) in paragraph" :key="`${pIndex}-${index}`"
                :data-index="getGlobalIndex(pIndex, index)" :class="[
                  'curriculum-word',
                  {
                    selected: selectedIndexes.includes(getGlobalIndex(pIndex, index)),
                    evidenziata: indexAssociati.has(getGlobalIndex(pIndex, index)),
                    noSpace: /^[.,:;!?-]+$/.test(word)
                  }
                ]" @mouseover="handleHover(getGlobalIndex(pIndex, index))">
                {{ word }}
              </span>

            </p>
          </div>
        </div>

      </div>

      <!-- Colonna sinistra con i campi -->
      <div class="left-panel">
        <div v-for="(fields, category) in fieldsByCategory" :key="category">
          <h3>
            {{ categoryLabels[category] }}
            <button @click="openAddCampo(category)">➕ Aggiungi</button>
          </h3>

          <!-- Solo se la categoria è attiva -->
          <div v-if="categoriaInAggiunta === category" class="add-campo">
            <input v-model="newFields[category]" placeholder="Nuovo campo..." />
            <button @click="confermaAggiuntaCampo(category)">Aggiungi</button>
            <button @click="annullaAggiuntaCampo()">Annulla</button>
          </div>

          <ul>
            <li v-for="(field, idx) in fields" :key="idx" @click="selectCampo(field)"
              :class="{ selectedCampo: selectedCampo === field }">
              {{ field }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Colonna laterale -->
      <div class="side-panel">
        <h2>TRAINING</h2>

        <p v-if="selectedCampo">Campo selezionato: <strong>{{ selectedCampo }}</strong></p>
        <p v-if="selectionText">Hai selezionato: <strong>"{{ selectionText }}"</strong></p>
        <p v-else class="placeholder">Seleziona una o più parole dal curriculum...</p>

        <label>Voto:</label>
        <div style="position: relative; display: inline-block;">
          <div class="voto-selezione" @click="votoPopupVisible = !votoPopupVisible">
            <span>{{ voto !== null ? voto : '' }}</span>
          </div>
          <div v-if="votoPopupVisible" class="voto-popup">
            <span v-for="n in 11" :key="n - 1" @click="selectVoto(n - 1)">
              {{ n - 1 }}
            </span>
          </div>
        </div>

        <button :disabled="!selectedCampo || !selectionText || voto === null || voto === ''" @click="salvaTraining">
          Salva
        </button>


        <div class="log">
          <h3>Training registrato:</h3>
          <ul>
            <li v-for="(comp, index) in comparazioni" :key="index">
              {{ comp.text1 }} - {{ comp.text2 }} ({{ comp.score }}/10)
              <button @click="rimuoviComparazione(index)" style="margin-left: 8px;">🗑</button>
            </li>
          </ul>
          <button v-if="comparazioni.length > 0" @click="inviaComparazioniAlBackend" style="margin-top: 10px;">
            Salva il training
          </button>
        </div>
      </div>
      <!-- MODALE DI MODIFICA TESTO -->
      <div v-if="showTextEditor" class="text-editor-modal" @click.self="closeEditor">
        <div class="text-editor-box">
          <h3>Modifica il testo del curriculum</h3>
          <textarea v-model="editableText" rows="15" style="width: 100%;"></textarea>
          <div class="text-editor-buttons">
            <button @click="applyTextChanges">Salva le modifiche</button>
            <button @click="closeEditor">Annulla</button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      curriculumText: '',
      isSelecting: false,
      hasDragged: false,
      selectedIndexes: [],
      selectedCategory: '',
      tipoCurriculum: this.$route.params.tipoCurriculum,
      voto: null,
      log: [],
      toggledDuringDrag: new Set(),
      votoPopupVisible: false,
      fieldsByCategory: {
        titoli: [],
        competenze: [],
        esperienze: []
      },
      newFields: {
        titoli: '',
        competenze: '',
        esperienze: ''
      },
      selectedType: '',
      categoryLabels: {
        titoli: 'Titoli di studio',
        competenze: 'Competenze',
        esperienze: 'Esperienze'
      },
      selectedCampo: '',
      comparazioni: [],
      indexAssociati: new Set(),
      categoriaInAggiunta: null,
      trainingData: {},
      showFullPdf: false,
      pdfUrl: '',
      pdfName: '',
      isEditing: false,
      hasChanges: false,
      showTextEditor: false,
      editableText: ""
    };
  },

  created() {
    const savedText = localStorage.getItem('curriculumText');
    if (savedText) {
      this.curriculumText = savedText;
    } else {
      this.curriculumText = `Questo è un esempio di curriculum. Laurea in ingengeria informatica, esperienza con linguaggi di programmazione quali Java e Python `;
    }
    const fields = sessionStorage.getItem('filteredFields');
    const type = sessionStorage.getItem('selectedType');

    if (fields) {
      this.fieldsByCategory = JSON.parse(fields);
    }
    if (type) {
      this.selectedType = type;
    }

  },

  beforeDestroy() {
    localStorage.removeItem('curriculumText');
  },

  computed: {
    words() {
      return this.curriculumText.match(/[A-Za-zÀ-ÿ0-9+#]+|[.,:;!?()'"-]/g) || [];
    },

    selectionText() {
      return [...this.selectedIndexes]
        .sort((a, b) => a - b)
        .map(i => this.words[i])
        .join(' ');
    },

    paragraphs() {
      if (!this.curriculumText) return [];

      return this.curriculumText
        .split('\n\n')
        .map(paragraph =>
          paragraph.match(/[A-Za-zÀ-ÿ0-9+#]+|[.,:;!?()'"-]/g) || []
        );
    },

    flatWords() {
      return this.paragraphs.flat();
    }
  },

  methods: {
    toggleWord(index) {
      const flatWords = this.paragraphs.flat();
      if (!flatWords[index]) {
        console.warn(`Indice ${index} fuori dai limiti (${flatWords.length})`);
        return;
      }
      let parola = this.words[index].trim().replace(/^[.,:;!?()'"-]+|[.,:;!?()'"-]+$/g, '');
      parola = parola.toLowerCase();

      let match = null;
      for (const categoria in this.trainingData) {
        match = this.trainingData[categoria].find(
          entry =>
            entry.text1 === this.selectedCampo &&
            entry.text2.toLowerCase().replace(/^[.,:;!?()'"-]+|[.,:;!?()'"-]+$/g, '') === parola
        );
        if (match) {
          this.selectedCategory = categoria;
          break;
        }
      }

      if (match) {
        this.voto = match.score * 10;
      }

      if (this.selectedIndexes.includes(index)) {
        this.selectedIndexes = this.selectedIndexes.filter(i => i !== index);
      } else {
        this.selectedIndexes.push(index);
      }
    },

    startSelection() {
      this.isSelecting = true;
      this.hasDragged = false;
      this.toggledDuringDrag = new Set();
    },

    endSelection(event) {
      this.isSelecting = false;

      if (!this.hasDragged) {
        const target = event.target;
        if (target && target.tagName === 'SPAN' && target.hasAttribute('data-index')) {
          const index = parseInt(target.getAttribute('data-index'));
          this.toggleWord(index);
        }
      }
    },

    handleHover(index) {
      if (this.isSelecting && !this.toggledDuringDrag.has(index)) {
        this.hasDragged = true;
        if (this.selectedIndexes.includes(index)) {
          this.selectedIndexes = this.selectedIndexes.filter(i => i !== index);
        } else {
          this.selectedIndexes.push(index);
        }
        this.toggledDuringDrag.add(index);
      }
    },

    selectVoto(n) {
      this.voto = n;
      this.votoPopupVisible = false;
    },


    salvaTraining() {
      const categoriaCorretta = Object.entries(this.fieldsByCategory).find(
        ([, campi]) => campi.includes(this.selectedCampo)
      )?.[0];

      const parolaSelezionata = this.selectionText;

      if (!categoriaCorretta || !parolaSelezionata || !this.selectedCampo || this.voto === null) {
        alert("Uno o più dati mancanti! Seleziona un campo, una parola e assegna un voto.");
        return;
      }

      this.comparazioni.push({
        categoria: categoriaCorretta,
        text1: this.selectedCampo,
        text2: parolaSelezionata,
        score: this.voto
      });

      this.log.push({
        frase_selezionata: this.selectionText,
        categoria: categoriaCorretta,
        valutazione: this.voto,
        commento: this.commento
      });

      this.selectedIndexes = [];
      this.selectedCategory = '';
      this.voto = null;
      this.commento = '';

      localStorage.removeItem('curriculumText');

      sessionStorage.setItem('comparazioni', JSON.stringify(this.comparazioni));

      console.log("Comparazione salvata:", this.comparazioni[this.comparazioni.length - 1]);
    },

    selectCampo(campo) {
      this.selectedCampo = campo;

      let matched = [];
      for (const categoria in this.trainingData) {
        this.trainingData[categoria].forEach(entry => {
          if (entry.text1 === campo) {
            matched.push({ ...entry, categoria });
          }
        });
      }


      this.indexAssociati = new Set();

      matched.forEach(entry => {
        const normalized = (str) => str.toLowerCase().replace(/[^\wÀ-ÿ0-9]+/g, ' ').trim();
        const entryWords = normalized(entry.text2).split(" ");
        const wordsNormalized = this.words.map(w => normalized(w));

        for (let i = 0; i <= wordsNormalized.length - entryWords.length; i++) {
          const slice = wordsNormalized.slice(i, i + entryWords.length);
          if (JSON.stringify(slice) === JSON.stringify(entryWords)) {
            for (let j = 0; j < entryWords.length; j++) {
              this.indexAssociati.add(i + j);
            }
          }
        }
      });
    },

    isParolaAssociata(index) {
      return this.comparazioni.some(entry => entry.parole && entry.parole.includes(index));
    },

    getCategoriaFromCampo(campo) {
      for (const [cat, fields] of Object.entries(this.fieldsByCategory)) {
        if (fields.includes(campo)) return cat;
      }
      return '';
    },

    openAddCampo(category) {
      this.categoriaInAggiunta = category;
      this.newFields[category] = '';
    },

    async confermaAggiuntaCampo(category) {
      const nuovo = this.newFields[category].trim();
      if (!nuovo) return;

      if (!this.fieldsByCategory[category].includes(nuovo)) {
        this.fieldsByCategory[category].push(nuovo);
      }

      try {
        const res = await fetch(`/api/custom-fields/${this.selectedType}/add`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            categoria: category,
            campo: this.newFields[category]
          })
        });


        if (!res.ok) throw new Error("Errore nella richiesta al backend");
      } catch (err) {
        console.error("Errore durante il salvataggio:", err);
      }

      this.newFields[category] = '';
      this.categoriaInAggiunta = null;
    },

    annullaAggiuntaCampo() {
      if (this.categoriaInAggiunta) {
        this.newFields[this.categoriaInAggiunta] = '';
        this.categoriaInAggiunta = null;
      }
    },

    rimuoviComparazione(index) {
      this.comparazioni.splice(index, 1);
      sessionStorage.setItem('comparazioni', JSON.stringify(this.comparazioni));
    },

    getParolaSelezionata(indexes) {
      if (!indexes || indexes.length === 0) return '';
      return indexes.map(i => this.words[i]).join(' ');
    },

    async inviaComparazioniAlBackend() {
      if (this.comparazioni.length === 0) return;

      try {
        const csrfToken = this.getCookie("csrftoken");

        const payload = this.comparazioni.map(comp => ({
          categoria: comp.categoria,
          text1: comp.text1,
          text2: comp.text2,
          score: comp.score
        }));

        console.log("Invio dati al backend:", JSON.stringify(payload, null, 2));

        const res = await fetch("/api/train-data/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
          },
          credentials: "include",
          body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Errore durante il salvataggio nel backend");

        await this.inviaTrainRecognize();
        await this.inviaTrainQuestions();

        this.comparazioni = [];
        sessionStorage.removeItem("comparazioni");

        alert("Training salvato con successo!");
        this.$router.push("/");
      } catch (err) {
        console.error("Errore durante il salvataggio:", err);
        alert("Errore durante il salvataggio del training");
      }
    },

    async inviaTrainRecognize() {
      const recognizeData = this.comparazioni.map(comp => {
        const text = this.curriculumText;
        const selected = comp.text2;

        const pos = text.indexOf(selected);
        if (pos === -1) return null;

        const inizio = Math.max(text.lastIndexOf('.', pos), text.lastIndexOf('\n', pos), 0);
        const finePunto = text.indexOf('.', pos);
        const fineACapo = text.indexOf('\n', pos);
        let fine = text.length;

        if (finePunto !== -1 && fineACapo !== -1)
          fine = Math.min(finePunto, fineACapo);
        else if (finePunto !== -1)
          fine = finePunto;
        else if (fineACapo !== -1)
          fine = fineACapo;

        const frase = text.slice(inizio === 0 ? 0 : inizio + 1, fine).trim();

        const start = frase.indexOf(selected);
        if (start === -1) return null;

        return {
          frase: frase,
          start: start,
          end: start + selected.length,
          categoria: comp.categoria
        };
      }).filter(Boolean);

      if (recognizeData.length === 0) return;

      try {
        const res = await fetch("/api/train-recognize/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: "include",
          body: JSON.stringify(recognizeData)
        });

        if (!res.ok) throw new Error("Errore nel salvataggio recognize");

      } catch (e) {
        console.error("Errore in inviaTrainRecognize:", e);
        alert("Errore nel salvataggio del training recognize");
      }
    },

    async inviaTrainQuestions() {
      const questions = this.comparazioni.map(comp => {
        const testo = comp.text2;
        const categoria = comp.categoria;
        let domanda = "";

        if (categoria === "titoli_di_studio") {
          if (/laurea/i.test(testo)) {
            domanda = `Hai una laurea in ${testo}?`;
          } else if (/diploma/i.test(testo)) {
            domanda = `Hai un diploma di ${testo}?`;
          } else {
            domanda = `Hai un titolo di studio in ${testo}?`;
          }
        } else if (categoria === "competenze") {
          domanda = `Hai competenze in ${testo}?`;
        } else if (categoria === "esperienze") {
          const primaParola = testo.trim().split(" ")[0] || "";
          if (primaParola.toLowerCase().endsWith("zione")) {
            domanda = `Hai esperienza nella ${testo}?`;
          }
          else if (primaParola.toLowerCase()=="sviluppo") {
            domanda = `Hai esperienza nello ${testo}?`;
          }
          else if (primaParola.toLowerCase()=="gestione") {
            domanda = `Hai esperienza nella ${testo}?`;
          }
          else {
            domanda = `Hai esperienza come ${testo}?`;
          }
        }

        return {
          categoria,
          testo,
          domanda
        };
      });

      if (questions.length === 0) return;

      try {
        const res = await fetch("/api/train-questions/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(questions)
        });

        if (!res.ok) throw new Error("Errore nel salvataggio trainQuestions");

      } catch (e) {
        console.error("Errore in inviaTrainQuestions:", e);
        alert("Errore nel salvataggio del training questions");
      }
    },

    getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(";").shift();
      return "";
    },

    openPdf() {
      this.showFullPdf = true;
    },

    closePdf() {
      this.showFullPdf = false;
    },

    startEditing() {
      this.isEditing = true;
    },

    saveText() {
      sessionStorage.setItem('curriculumText', this.curriculumText);
      this.hasChanges = false;
      this.isEditing = false;
    },

    openEditor() {
      this.editableText = this.curriculumText;
      this.showTextEditor = true;
    },

    closeEditor() {
      this.showTextEditor = false;
    },

    applyTextChanges() {
      this.curriculumText = this.editableText;
      this.showTextEditor = false;
      sessionStorage.setItem("curriculumText", this.curriculumText);
      this.hasChanges = false;
    },

    getWordsWithOffset(paragraph, pIndex) {
      const paragraphWords = paragraph.match(/[A-Za-zÀ-ÿ0-9+#]+|[.,:;!?()'"-]/g) || [];
      const offset = this.paragraphs
        .slice(0, pIndex)
        .reduce((sum, p) => {
          return sum + (p.match(/[A-Za-zÀ-ÿ0-9+#]+|[.,:;!?()'"-]/g) || []).length;
        }, 0);
      return paragraphWords.map((w, i) => {
        const index = offset + i;
        return {
          word: w,
          index: index
        };
      });
    },

    getGlobalIndex(pIndex, wIndex) {
      let index = 0;
      for (let i = 0; i < pIndex; i++) {
        index += this.paragraphs[i].length;
      }
      return index + wIndex;
    },


  },

  async mounted() {
    window.addEventListener('mouseup', this.endSelection);
    try {
      await fetch("/api/get-csrf-token/", {
        credentials: "include"
      });
    } catch (err) {
      console.error("Errore nel recupero del token CSRF:", err);
    }

    const storedType = sessionStorage.getItem('selectedType');
    if (storedType) {
      this.selectedType = storedType;

      try {
        const res = await fetch(`/api/custom-fields/${storedType}/`);
        if (!res.ok) throw new Error("Errore nel recupero dei campi");
        const data = await res.json();
        this.fieldsByCategory = data;
      } catch (err) {
        console.error("Errore durante il caricamento dei campi personalizzati:", err);
      }
    }

    const savedText = sessionStorage.getItem('curriculumText');
    if (savedText) {
      this.curriculumText = savedText;
    } else {
      this.curriculumText = `Mario Rossi ha ottenuto la laurea in Informatica...`;
    }

    const trainingRes = await fetch("http://localhost:8000/api/train-data/");
    const data = await trainingRes.json();
    this.trainingData = data;

    const storedComparazioni = sessionStorage.getItem('comparazioni');
    if (storedComparazioni) {
      try {
        let parsed = JSON.parse(storedComparazioni);
        this.comparazioni = parsed.filter(comp => {
          const lista = this.trainingData?.[comp.categoria] || [];
          return lista.some(entry =>
            entry.text1 === comp.text1 && entry.text2 === comp.text2
          );
        });
      } catch (e) {
        console.error("Errore nel parsing di comparazioni da sessionStorage:", e);
      }
    }

    const storedPdfUrl = sessionStorage.getItem('pdfUrl');
    const storedPdfName = sessionStorage.getItem('pdfName');

    if (storedPdfUrl && storedPdfName) {
      this.pdfUrl = storedPdfUrl;
      this.pdfName = storedPdfName;
    }
  }
};
</script>

<style scoped>
html, body {
  height: 100%;
  margin: 0;
  overflow: hidden;
}

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: #e0e0e0;
  border-bottom: 1px solid #b0b0b0;
  padding: 10px 20px;
  z-index: 999;
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.navbar a {
  margin: 0 10px;
  color: #333;
  text-decoration: none;
  font-weight: bold;
}

.navbar a:hover {
  text-decoration: underline;
}

.training-container {
  display: flex;
  position: fixed;
  height: 100vh;
  overflow: hidden;
  padding-top: 60px;
  box-sizing: border-box;
}


.left-panel {
  position: fixed;
  top: 30px;
  left: 0;
  width: 250px;
  background-color: #f9f9f9;
  border-right: 1px solid #ddd;
  height: calc(100vh - 60px);
  overflow-y: auto;
  padding: 15px;
  font-family: 'Segoe UI', sans-serif;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 40px;
  margin-left: 260px;
  margin-right: 300px;
  max-width: unset;
  word-wrap: break-word;
  overflow-wrap: break-word;
  height: 100%;
  box-sizing: border-box;
}

.side-panel {
  position: fixed;
  top: 30px;
  right: 0;
  width: 300px;
  height: calc(100vh - 60px);
  background-color: #f3f3f3;
  padding: 20px;
  padding-top: 2%;
  border-left: 2px solid #ddd;
  overflow-y: auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.placeholder {
  font-size: 99%;
}


span {
  margin-right: 5px;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

span.selected {
  background-color: #cce5ff;
}

.voto-selezione {
  width: 30px;
  height: 30px;
  background-color: #fff;
  border: 1px solid #ccc;
  text-align: center;
  line-height: 30px;
  font-weight: bold;
  cursor: pointer;
  display: inline-block;
  margin-left: 5px;
}


.voto-selezione .placeholder {
  color: #aaa;
}

.voto-popup {
  position: absolute;
  background: #fff;
  border: 1px solid #ccc;
  padding: 5px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  margin-top: 5px;
  z-index: 1000;
}

.voto-popup span {
  padding: 6px;
  cursor: pointer;
}

.voto-popup span:hover {
  background-color: #e0e0e0;
}

.selectedCampo {
  background-color: #d0e8ff;
  font-weight: bold;
  cursor: pointer;
}

.left-panel li {
  cursor: pointer;
  padding: 4px;
}

.evidenziata {
  background-color: #b2f2bb;
}

.pdf-preview-training {
  border: 2px dashed #aaa;
  padding: 10px;
  margin-bottom: 20px;
  cursor: pointer;
  width: 30%;
  max-width: 100%;
  font-weight: bold;
  display: inline-block;
}

.mini-pdf-box {
  display: inline-block;
  margin-bottom: 10px;
  border: 1px dashed #aaa;
  background-color: #f9f9f9;
  font-weight: bold;
  font-size: 14px;
  cursor: pointer;
  padding: 6px 12px;
  transition: background-color 0.2s;
}

.mini-pdf-box:hover {
  background-color: #e0e0e0;
}

.pdf-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.text-editor-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.text-editor-box {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 600px;
  max-width: 90%;
}

.text-editor-buttons {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.noSpace {
  margin-right: 0;
  ;
}

.curriculum-paragraph {
  margin-bottom: 1em;
  line-height: 1.6;
  text-align: justify;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

span.curriculum-word {
  display: inline-block;
  margin-right: 0.10em;
  white-space: normal;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  cursor: pointer;
}

.curriculum-word.noSpace {
  margin-right: 0;
}

</style>