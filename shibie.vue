<template>
  <div id="app">
    <h1 style="text-align: center;">图像上传与预测</h1>
    <div class="container">
      <div class="upload">
        <div @drop.prevent="onDrop" @paste.prevent="onPaste" @click="onClick"
             class="drop-zone" tabindex="0">
          <div v-if="previewImage" class="preview-container">
            <img :src="previewImage" alt="预览图像" class="preview-image" />
          </div>
          <div v-else>
            拖拽图片到这里或点击选择
          </div>
        </div>
        <button @click="uploadImage('cat')" style="margin: 20px auto; display: block;">上传猫的图片并预测</button>
        <button @click="uploadImage('dog')" style="margin: 20px auto; display: block;">上传狗的图片并预测</button>
      </div>
      
      <div class="result">
        <h2>预测结果</h2>
        <div v-if="loading" class="loading">加载中...</div>
        <div v-if="message" class="result-container">
          <p><strong>品种：</strong> {{ breed }}</p>
          <p><strong>详细信息：</strong></p>
          <p>{{ breedInfo }}</p>
          <img v-if="resultImage" :src="resultImage" alt="预测结果" class="result-image" />
        </div>
      </div>
      <div class="history">
        <h2>历史识别</h2>
        <div v-if="history.length === 0" class="no-history">暂无历史记录</div>
        <ul class="history-list">
          <li v-for="(item, index) in history" :key="index">
            <img :src="item.resultImage" alt="历史预测图像" class="history-image">
            <div class="history-details">
              <p><strong>品种：</strong>{{ item.breed }}</p>
              <p>{{ item.breedInfo }}</p>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedFile: null,
      previewImage: '',
      message: '',
      resultImage: '',
      breed: '',
      breedInfo: '',
      loading: false,
      history: [],
    };
  },
  methods: {
    onClick() {
      const fileInput = document.createElement('input');
      fileInput.type = 'file';
      fileInput.accept = 'image/*';
      fileInput.onchange = e => {
        this.selectedFile = e.target.files[0];
        this.previewImage = URL.createObjectURL(this.selectedFile);
      };
      fileInput.click();
    },
    onDrop(event) {
      this.selectedFile = event.dataTransfer.files[0];
      this.previewImage = URL.createObjectURL(this.selectedFile);
    },
    onPaste(event) {
      const items = (event.clipboardData || event.originalEvent.clipboardData).items;
      for (const item of items) {
        if (item.type.indexOf('image') === 0) {
          this.selectedFile = item.getAsFile();
          this.previewImage = URL.createObjectURL(this.selectedFile);
        }
      }
    },
    async uploadImage(animalType) { // 修改了这里
      if (!this.selectedFile) {
        alert('请先选择一个图像文件');
        return;
      }
      const formData = new FormData();
      formData.append('file', this.selectedFile);
      this.loading = true;
      try {
        const response = await fetch(`http://localhost:5000/predict/${animalType}`, { // 修改了这里
          method: 'POST',
          body: formData,
        });
        if (!response.ok) {
          throw new Error('网络响应不正常');
        }
        const result = await response.json();
        this.loading = false;
        if (result.predictions && result.predictions.length > 0) {
          const prediction = result.predictions[0];
          this.breed = prediction.breed;
          this.breedInfo = prediction.breedInfo;
          this.resultImage = `data:image/jpeg;base64,${result.image}`;
          this.message = '宠物识别成功！';
          this.history.push({
            breed: this.breed, breedInfo: this.breedInfo, resultImage: this.resultImage
          });
        } else {
          this.message = '没有检测到任何宠物。';
        }
      } catch (error) {
        console.error('上传图像时出错:', error);
        this.message = '上传图像时出错: ' + error.message;
        this.loading = false;
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
/* 你的样式保持不变 */
</style>


<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: #f3f7f7;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  margin: 30px auto;
}
h1, h2 {
  color: #333;
}
.upload, .result, .history {
  width: 100%;
  padding: 20px;
  background: rgb(233, 231, 231);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-top: 20px;
}
button {
  background-color: #82b753;
  color: white;
  border: none;
  padding: 12px 24px; /* 加大按钮尺寸 */
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
button:hover {
  background-color: #0ea24e;
}
.drop-zone {
  padding: 10px;
  border: 2px dashed #8a1fc4;
  border-radius: 5px;
  width: 100%;
  text-align: center;
  cursor: pointer;
  min-height: 300px;
  color: #bbb;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  position: relative;
}
.preview-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}
.preview-image {
  max-width: 100%;
  max-height: 100%;
}
.drop-zone:focus {
  outline: none;
}
.result-container, .history-list {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
  text-align: left;
  color: #444;
}
.result-image, .history-image {
  max-width: 100%;
  border-radius: 8px;
  margin-top: 15px;
}
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50px;
}
.loading::after {
  content: "";
  width: 25px;
  height: 25px;
  border: 4px solid #2100f9;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
.pet-type-selection {
  margin-top: 20px;
  text-align: center;
}
.pet-option {
  background-color: #ffffff;
  border: 2px solid #82b753;
  color: #333;
  padding: 15px 30px; /* 更进一步加大按钮尺寸 */
  border-radius: 5px;
  cursor: pointer;
  margin-right: 10px;
  transition: background-color 0.3s ease, color 0.3s ease;
}
.pet-option:hover {
  background-color: #82b753;
  color: #ffffff;
}
</style>
