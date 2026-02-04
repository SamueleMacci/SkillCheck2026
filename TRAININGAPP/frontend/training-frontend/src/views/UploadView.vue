<template>
    <div class="upload-container">
        <h2>Carica Curriculum (PDF)</h2>
        <input type="file" @change="handleFileChange" accept="application/pdf" />
        <button @click="uploadPDF" :disabled="!pdfFile">Carica</button>

        <div v-if="extractedText">
            <h3>Testo Estratto:</h3>
            <pre>{{ extractedText }}</pre>
        </div>

        <div v-if="error" class="error">{{ error }}</div>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    data() {
        return {
            pdfFile: null,
            extractedText: '',
            error: ''
        }
    },
    methods: {
        handleFileChange(event) {
            this.pdfFile = event.target.files[0]
            this.extractedText = ''
            this.error = ''
        },
        async uploadPDF() {
            if (!this.pdfFile) return;

            const formData = new FormData();
            formData.append('file', this.pdfFile);

            try {
                const response = await axios.post('http://localhost:8000/api/parse-pdf/', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                });

                const extractedText = response.data.text;

                const reader = new FileReader();
                reader.onload = () => {
                    const pdfUrl = reader.result;

                    sessionStorage.setItem('pdfUrl', pdfUrl);
                    sessionStorage.setItem('pdfName', this.pdfFile.name);
                    sessionStorage.setItem('curriculumText', extractedText);

                    this.$router.push('/curriculum-details');
                };

                reader.readAsDataURL(this.pdfFile);

            } catch (err) {
                this.error = 'Errore durante l\'upload o parsing del PDF';
            }
        }



    }
}
</script>

<style scoped>
.upload-container {
    text-align: center;
    max-width: 600px;
    margin: 40px auto;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;

}

.error {
    color: red;
}
</style>
