<template>
    <div class="curriculum-details-container">
        <!-- Sezione Top -->
        <div class="top-section">
            <!-- Anteprima PDF -->
            <div class="pdf-preview" @click="showFullPdf = true">
                <p v-if="!pdfName">Nessun file PDF caricato</p>
                <p v-else>{{ pdfName }} (clicca per aprire)</p>
            </div>


            <!--Visualizzazione completa PDF -->
            <div v-if="showFullPdf" class="pdf-modal" @click.self="showFullPdf = false">
                <embed :src="pdfUrl" type="application/pdf" width="80%" height="600px" />
            </div>

            <!-- Selezione Tipo Curriculum -->
            <div class="curriculum-type">
                <label>Tipo di curriculum:</label>
                <select v-model="selectedType" @change="onTipoCurriculumChange">
                    <option v-for="type in tipologieDisponibili" :key="type" :value="type">
                        {{ type }}
                    </option>
                </select>

                <input v-model="newType" placeholder="Nuovo tipo..." />
                <button @click="addCurriculumType">Aggiungi</button>
            </div>
        </div>

        <!-- Vai al training -->
        <button @click="proceedToTraining">Vai al Training</button>
        <button @click="toggleDeleteMode">Elimina campi</button>

        <!-- Categorie -->
        <div class="categories-section">
            <div class="category-box" v-for="(items, key) in categoryFields" :key="key">
                <h3>{{ categoryLabels[key] }}:</h3>
                <ul>
                    <li v-for="(item, index) in items" :key="index">
                        {{ item }}
                        <button v-if="showDeleteButtons" @click="removeField(key, item)">🗑️</button>
                        <hr style="border: none; border-bottom: 1px solid #ccc; margin: 2px 0;" />
                    </li>
                </ul>

                <input v-model="newFields[key]" placeholder="Aggiungi..." />
                <button @click="addField(key)">Aggiungi</button>
            </div>
        </div>

    </div>
</template>

<script>
export default {
    data() {
        return {
            pdfUrl: '',
            pdfName: '',
            showFullPdf: false,

            selectedType: '',
            newType: '',
            tipologieDisponibili: [],
            showDeleteButtons: false,

            categoryLabels: {
                titoli: 'Titoli di studio richiesti o consigliati',
                competenze: 'Competenze richieste o consigliate',
                esperienze: 'Esperienze richieste o consigliate',
            },

            categoryFields: {
                titoli: [],
                competenze: [],
                esperienze: []
            },

            newFields: {
                titoli: '',
                competenze: '',
                esperienze: ''
            },

            userAddedFields: {
                titoli: [],
                competenze: [],
                esperienze: []
            },
            campiPersonalizzati: {}
        };
    },

    methods: {
        async addCurriculumType() {
            const newType = this.newType.trim();
            if (!newType || this.tipologieDisponibili.includes(newType)) return;

            try {
                await fetch("http://localhost:8000/api/custom-fields/add-type", {
                    method: "POST",
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tipo: newType })
                });

                await this.fetchTipologieDisponibili();

                this.selectedType = newType;
                this.newType = '';
            } catch (err) {
                console.error("Errore durante la creazione del nuovo tipo:", err);
            }
        },

        async addField(category) {
            const field = this.newFields[category].trim();
            if (field && !this.categoryFields[category].includes(field)) {
                this.categoryFields[category].push(field);
                this.userAddedFields[category].push(field);
                this.newFields[category] = '';

                try {
                    await fetch(`http://localhost:8000/api/custom-fields/${this.selectedType}/add`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            categoria: category,
                            campo: field
                        })
                    });
                } catch (error) {
                    console.error('Errore nel salvataggio backend:', error);
                }
            }
        },

        async removeField(category, field) {
            this.categoryFields[category] = this.categoryFields[category].filter(f => f !== field);

            this.userAddedFields[category] = this.userAddedFields[category].filter(f => f !== field);

            try {
                await fetch(`http://localhost:8000/api/custom-fields/${this.selectedType}/remove`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        categoria: category,
                        campo: field
                    })
                });
            } catch (error) {
                console.error('Errore durante la rimozione del campo:', error);
            }
        },

        isUserField(field) {
            return Object.values(this.userAddedFields).some(arr => arr.includes(field));
        },

        proceedToTraining() {
            sessionStorage.setItem('selectedType', this.selectedType);

            const filteredFields = {};
            for (const key in this.categoryFields) {
                filteredFields[key] = this.categoryFields[key];
            }
            sessionStorage.setItem('filteredFields', JSON.stringify(filteredFields));

            sessionStorage.setItem('userAddedFields', JSON.stringify(this.userAddedFields));

            this.$router.push(`/training/${this.selectedType}`);
        },

        async fetchCampiPersonalizzati(tipologia) {
            if (!tipologia) return;

            try {
                const res = await fetch(`http://localhost:8000/api/custom-fields/${encodeURIComponent(tipologia)}`);
                if (!res.ok) throw new Error('Errore nel recupero dei campi personalizzati');

                const data = await res.json();

                this.categoryFields = {
                    titoli: data.titoli || [],
                    competenze: data.competenze || [],
                    esperienze: data.esperienze || []
                };
            } catch (error) {
                console.error('Errore durante fetchCampiPersonalizzati:', error);
                this.categoryFields = { titoli: [], competenze: [], esperienze: [] };
            }
        },

        async fetchTipologieDisponibili() {
            try {
                const res = await fetch('http://localhost:8000/api/custom-fields/');
                const data = await res.json();
                console.log("Tipologie ricevute dal backend:", data);
                this.tipologieDisponibili = data.types || [];
            } catch (error) {
                console.error('Errore durante fetchTipologieDisponibili:', error);
                this.tipologieDisponibili = [];
            }
        },

        onTipoCurriculumChange() {
            sessionStorage.setItem('selectedType', this.selectedType);
        },

        toggleDeleteMode() {
            const hasFields =
                this.categoryFields.titoli.length > 0 ||
                this.categoryFields.competenze.length > 0 ||
                this.categoryFields.esperienze.length > 0;

            if (!hasFields) return;

            this.showDeleteButtons = !this.showDeleteButtons;
        },

        vaiAlTraining() {
            if (!this.tipoCurriculum) {
                alert("Seleziona un tipo di curriculum prima di procedere.");
                return;
            }

            this.$router.push(`/training/${this.tipoCurriculum}`);
        },

    },

    async mounted() {
        await this.fetchTipologieDisponibili();
        const url = sessionStorage.getItem('pdfUrl');
        const name = sessionStorage.getItem('pdfName');
        console.log('pdfUrl from sessionStorage:', url);
        console.log('pdfName from sessionStorage:', name);

        if (url && name) {
            this.pdfUrl = url;
            this.pdfName = name;
            console.log("DEBUG - pdfUrl:", this.pdfUrl);
        }

        const storedType = sessionStorage.getItem('selectedType');
        if (storedType) {
            this.selectedType = storedType;
        }
    },

    watch: {
        selectedType: {
            immediate: true,
            async handler(newType) {
                if (!newType) return;

                console.log("WATCHER TRIGGERED! Tipo selezionato:", newType);

                try {
                    const res = await fetch(`/api/custom-fields/${newType}/`);
                    const data = await res.json();

                    console.log("DEBUG - campi ricevuti dal backend:", data);

                    this.campiPersonalizzati[newType] = data;

                    this.categoryFields = {
                        titoli: data.titoli || [],
                        competenze: data.competenze || [],
                        esperienze: data.esperienze || []
                    };

                } catch (err) {
                    console.error("Errore nel caricamento dei campi personalizzati:", err);
                }
            }
        }
    }



};
</script>

<style scoped>
.curriculum-details-container {
    padding: 20px;
    font-family: 'Segoe UI', sans-serif;
}

.top-section {
    display: flex;
    justify-content: space-between;
}

.pdf-preview {
    width: 45%;
    padding: 10px;
    border: 1px dashed #888;
    cursor: pointer;
}

.pdf-modal {
    position: fixed;
    top: 0;
    left: 0;
    background: rgba(0, 0, 0, 0.7);
    width: 100vw;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999;
}

.curriculum-type {
    width: 45%;
    display: flex;
    flex-direction: column;
}

.categories-section {
    display: flex;
    justify-content: space-around;
    margin-top: 30px;
}

.category-box {
    width: 30%;
}

.category-box ul {
    list-style-type: none;
    padding: 0;
}

li {
  margin: 2px 0;
  padding: 2px 0;
  font-size: 14px;
  line-height: 1.2;
}

</style>
