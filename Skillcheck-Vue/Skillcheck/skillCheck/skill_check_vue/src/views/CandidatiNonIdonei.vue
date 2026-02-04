<template>
    <div class="tabs-containerPadNonIdoneo">
        <div class="tabsNonIdoneo">
         <div class="contenutoAltoButton1">
          <button class="buttonVaiNonIdoneo" @click="goBack(id)"><img :src="imgCircleBack" width="60px" class="titoloLogoCandidati"/></button>
        </div>
        <div class="scrittaCandidatiNonIdonei">
          <h2>Candidati non idonei</h2>
        </div><br><br><br>
        <button class="buttonTabNonIdoneo"
          v-for="(item, index) in selectedItems" 
          :key="index" 
          :class="{ 'active': selectedItem === item }" 
          @click="selectedItem = item">
          {{ item.name }} 
        </button>
      </div>
      <div class="contentNonIdoneo" v-if="selectedItem">
        <br><br><br>
        <div class="EmailNonIdoneo">
          <h1>E-mail di rigetto</h1>
        </div>
        <div class="divContenutoEmailNonIdoneo">
          <p class="aDiPaginaNonIdoneo">A</p><button class="contenutoButtonPaginaNONIdoneo">{{ selectedItem.email }}</button>
        </div>
        <div class="divContenutoEmailNonIdoneo">
          <p class="OggettoDiPaginaNonIdoneo">Oggetto &nbsp;</p><button class="EsitoButtonPaginaNONIdoneo">Esito della tua candidatura -<h4>{{id}} </h4> &nbsp; preso &nbsp; <h4> AziendaX</h4></button>
        </div>
        <div>
          <button class="contenutoLungoButtonPaginaNONIdoneo">
            <p>Gentile <strong>{{selectedItem.name}}</strong></p>
            <p>Grazie di aver presentato la tua candidatura per la posizione <strong>{{id}}</strong>
            preso <strong>AziendaX</strong>. Dopo una valutazione approfondita, abbiamo considerato 
            un allineamento del <strong>6%</strong> tra il tuo CV e le tue risposte alla candidatura
            rispetto ai requiiti della posizione</p> <br><br>
            <p>Coordiali Saluti</p>
            <p><strong>Tizio Caio</strong></p>
            <p><strong>Hr Manager</strong></p>
          </button>
        </div>
        <div class="contenitoreButtonNonIdoonei">
          <div> 
            <button class="ScegliRispostaNonIdoneo">Scegli altra risposta</button>
          </div>
          <div> 
            <button class="InviaRispostaNonIdonea" >Invio </button>
          </div>

        </div>
      </div>
    </div>
</template>

<script>
export default {
  data() {
    return {
      selectedItems: [],
      selectedItem: null,
      imgCircleBack: require('@/assets/ArrowLeftIcon.png'),
      id:"Programmatore Softwore"
    };
  },
  created() {
    this.selectedItems = JSON.parse(this.$route.query.items || "[]");
    if (this.selectedItems.length) {
      this.selectedItem = this.selectedItems[0];
    }
  },
  methods: {
    goBack(id) {
      this.$router.push({ name: "Candidati", params: { id } });
    },
  }
};
</script>

<style>
.InviaRispostaNonIdonea{
  background: rgb(43, 42, 42);
  color: white;
  border: 2px solid rgb(43, 42, 42);
  height:100%;
  border-radius: 8px;
  width: 30%;
  margin-left: 395px;
}
.ScegliRispostaNonIdoneo{
  background: white;
  color: black;
  border: 2px solid rgb(43, 42, 42);
  height:100%;
  border-radius: 8px;
  width: 140%;
}
.contenitoreButtonNonIdoonei{
  display: flex;
  width: 70%;
  margin-left: 10%;
  margin-top:5%;
  height: 40px;
}
.divContenutoEmailNonIdoneo{
  display: flex;
}
.OggettoDiPaginaNonIdoneo{
  margin-left: 3%;
  margin-top: 2.5%;
}
.aDiPaginaNonIdoneo{
  margin-left: 8%;
  margin-top: 1.5%;
}
.EmailNonIdoneo{
  width: 50%;
  margin-left: 10%;
}
.contenutoLungoButtonPaginaNONIdoneo{
  margin-top: 2%;
  margin-left: 10%;
  height: 250px;
  background: rgb(216, 213, 213);
  border: none;
  padding-left: 10px;
  text-align:left;
  font-size: 16px;
  width: 70%;
  border-radius: 8px;
  padding: 5px;
}
.EsitoButtonPaginaNONIdoneo{
  margin-top: 2%;
  margin-left: 0%;
  height: 30px;
  background: rgb(216, 213, 213);
  border: none;
  padding-left: 10px;
  text-align:left;
  font-size: 16px;
  width: 60%;
  border-radius: 8px;
  display: flex;
  padding: 5px;
}
.contenutoButtonPaginaNONIdoneo{
  margin-top: 1%;
  margin-left: 1%;
  height: 30px;
  background: rgb(216, 213, 213);
  border: none;
  padding-left: 10px;
  text-align:left;
  font-size: 16px;
  width: 20%;
  border-radius: 8px;
}
.tabs-containerPadNonIdoneo {
  display: flex;
  width: 100%;
  height: 700px;
  overflow: hidden;
}

.tabsNonIdoneo{
  background-color: rgb(43, 42, 42);
  width: 30%;
  height: auto;
  display: flex;
  flex-direction: column;
}
.tabsNonIdoneo button.active {
  background-color:white;
  color: black;
  width: 93%;
}

.tabs div {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #ddd;
}

.tabs div.active {
  background: #007bff;
  color: white;
}

.contentNonIdoneo {
  width: 70%;
  padding: 20px;
  background: white;
}
.buttonTabNonIdoneo{
  background: white;
  padding: 20px;
  border: none;
  text-align:left;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
  margin-left: 10%;
  width: 80%;
  margin-top: 20px;
  border-radius: 10px;
  background: white;
}
.buttonVaiNonIdoneo{
  margin-top:5%;
  margin-left: 10%;
  background: white;
  border: none;
  border-radius: 50%;
}
.scrittaCandidatiNonIdonei{
  margin-left:40%;
  margin-top: -10%;
  color:white;
}
</style>