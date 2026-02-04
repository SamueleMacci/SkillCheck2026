<template>
  <div>
    <div class="home">
      <h1>Training per SkillCheck</h1>
      <router-link to="/upload" class="upload-link">Carica un curriculum</router-link>
    </div>
    <div class="info-box">
      <h2>ISTRUZIONI</h2>
      <p>
        <span class="number">1.</span> Carica un curriculum tramite questo link: <a href="/upload">carica un curriculum</a>
      </p>
      <p>
        <span class="number">2.</span> Nella pagina successiva potrai scegliere la tipologia di curriculum e i relativi campi (esperienze, competenze e titoli di studio richiesti)
      </p>
      <p>
        <span class="number">3.</span> Clicca su "Vai al Training" per proseguire alla pagina di training
      </p>
      <p>
        <span class="number">4.</span> Seleziona un campo di una delle tre categorie dalla colonna di sinistra <img src="@/assets/esempioCampo.jpg" alt="img" class="info-image-1" />
      </p>
      <p>
        <span class="number">5.</span> Seleziona una o più parole dal testo del curriculum (puoi selezionare una parola con un click o più parole tenendo premuto il tasto sinistro e scorrendo tra le parole). Puoi anche deselezionarle allo stesso modo <img src="@/assets/esempioCurriculum1.jpg" alt="img" class="info-image-2" />
      </p>
      <p>
        <span class="number">6.</span> Dai un voto alla comparazione e salva <img src="@/assets/esempioTraining.jpg" alt="img" class="info-image-3" />
      </p>
      <p>
        <span class="number">7.</span> Quando hai finito di fare il training per quel curriculum clicca su "Salva il training" <img src="@/assets/esempioSalva.jpg" alt="img" class="info-image-4" />
      </p>
    </div>
  </div>
</template>

<style scoped>
.home {
  text-align: center;
  margin-top: 10px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 30px;
}

.upload-link {
  font-size: 1.2rem;
  color: #007BFF;
  text-decoration: none;
}

.upload-link:hover {
  text-decoration: underline;
}

.info-box {
  text-align: left;
  font-family: Arial, sans-serif;
  border-radius: 8px;
}

.info-box h2 {
  font-size: 24px;
  margin-bottom: 10px;
}

.info-box p {
  font-size: 16px;
  line-height: 1.6;
}

.info-box a {
  color: #007bff;
  text-decoration: none;
}

.info-box a:hover {
  text-decoration: underline;
}

.info-image-1 {
  max-width: 15%;
  vertical-align:middle;
  border:3px dashed grey;
}

.info-image-2 {
  max-width: 20%;
  vertical-align:middle;
  border:3px dashed grey;
}

.info-image-3 {
  max-width: 13%;
  vertical-align:middle;
  border:3px dashed grey;
}

.info-image-4 {
  max-width: 15%;
  vertical-align:middle;
  border:3px dashed grey;
}

.number {
  font-size: 150%;
}
</style>

<script>
export default {
  name: 'HomeView',
}
</script>
