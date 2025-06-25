    // 保存功能相关元素
	const saveModal = document.getElementById('save-modal');
	const confirmSave = document.getElementById('confirm-save');
	const cancelSave = document.getElementById('cancel-save');
	const closeSaveModal = document.getElementById('close-save-modal');
	const modelSelect = document.querySelector('.model-select');
	const saveProjectSwitch = document.getElementById('save-project-switch');

    // 监听保存项目开关的点击事件
    saveProjectSwitch.addEventListener('click', function () {
      // 检查开关是否未被选中
      if (saveProjectSwitch.checked) {
        // 显示模态框
        saveModal.style.display = 'block';
      }
    });


	// 关闭模态框函数
	function closeSaveDialog() {
	  saveModal.style.display = "none";
	}

	// 事件监听
	closeSaveModal.addEventListener('click', closeSaveDialog);
	cancelSave.addEventListener('click', closeSaveDialog);

    // 监听确认保存按钮的点击事件
    confirmSave.addEventListener('click', async function () {
        const project_Name = document.getElementById('project-name').value.trim();

        // 检查项目名称是否为空
        if (!project_Name) {
            alert('请输入项目名称');
            return;
        }

        try {
            // 发送请求获取项目列表
            const result = await sendRequest('/project', 'GET', null);

            if (result.re_code === RET.OK) {
                // 检查项目名称是否冲突
                const isConflict = result.projects.some(project => project.project_name === project_Name);
                if (isConflict) {
                    alert('项目名称已存在，请更换');
                } else {
                    closeSaveDialog();
                }
            } else {
                console.error('Failed to load projects:', result.msg);
                alert('查询项目失败，请重试');
            }
        } catch (error) {
            console.error('请求错误:', error);
            alert('网络错误，请重试');
        }
    });

     // 封装函数：获取选中的值
    function getSelectedRadioValue(name) {
      const selectedRadio = document.querySelector(`input[name="${name}"]:checked`);
      return selectedRadio ? selectedRadio.value : null;
    }

    // 监听 tool1 的变化
    document.querySelectorAll('input[name="tool1"]').forEach(radio => {
      radio.addEventListener('change', (event) => {
        console.log('tool1 选中的值:', event.target.value);
      });
    });

    // 监听 tool2 的变化
    document.querySelectorAll('input[name="tool2"]').forEach(radio => {
      radio.addEventListener('change', (event) => {
        console.log('tool2 选中的值:', event.target.value);
      });
    });

    function toggleRadio(radio) {
	  if (radio.checked && radio.dataset.previouslyChecked === "true") {
	    // 如果当前是选中状态且之前已经被选中过，则取消选中
	    radio.checked = false;
	    radio.dataset.previouslyChecked = "false"; // 重置状态
	  } else {
	    // 否则设置为选中状态
	    radio.checked = true;
	    radio.dataset.previouslyChecked = "true"; // 标记为已选中
	  }
	}

    // <不同场景展示不同的目标类别>
	// 获取元素
    const showCategoriesBtn = document.getElementById('show-categories-btn'); // 打开模态框的按钮
    const categoryModal = document.getElementById('category-modal'); // 模态框
    const closeModalBtn = document.getElementById('close-modal-btn'); // 关闭模态框的按钮
    const sceneRadios = document.querySelectorAll('input[name="tool1"]'); // 场景选择单选框
    const categoryLists = document.querySelectorAll('.category-list'); // 所有类别列表

    let fileInput = document.getElementById('file-input');
    let originalImageContainer = document.getElementById('original-image-container');
    let detectionResultContainer = document.getElementById('detection-result');
    let totalContainer =document.getElementById('total-targets');
    let timeContainer =document.getElementById('detection-time');
    let detectButton = document.getElementById('detect-button');
    let hasImage = false;
    let uploadedImage = null;

    // 更新滑块显示
    const confThreshold = document.getElementById('conf-threshold');
    const confValue = document.getElementById('conf-value');
    confThreshold.addEventListener('input', function() {
      confValue.textContent = confThreshold.value;
      console.log("置信度滑块更新:", confThreshold.value);
    });

    function openFileDialog() {
      console.log("打开文件选择对话框");
      fileInput.click();
    }

    function displaySelectedImage() {
      const file = fileInput.files[0];
      if (file) {
        console.log("文件已选择:", file.name);
        const reader = new FileReader();
        reader.onload = function(e) {
          uploadedImage = e.target.result;
          console.log("文件读取完成，开始加载图片");
          const img = new Image();
          img.src = uploadedImage;
          img.onload = function() {
            console.log("图片加载完成");
            originalImageContainer.innerHTML = '';
            originalImageContainer.appendChild(img);
            hasImage = true;
          };
        };
        reader.readAsDataURL(file);
      } else {
        console.log("未选择文件");
      }
    }


    // 打开模态框
    showCategoriesBtn.addEventListener('click', () => {
      // 显示模态框
      categoryModal.style.display = 'flex';
      // 根据当前选中的场景更新类别显示
      updateCategoryDisplay();
    });

    // 关闭模态框
    closeModalBtn.addEventListener('click', () => {
      const selectedCategories = getSelectedCategories();

      // 检查是否选择了至少一个类别
      if (selectedCategories.length === 0) {
        alert('请选择至少一个类别');
        return;
      }
      categoryModal.style.display = 'none';
    });

    // 更新类别显示
    function updateCategoryDisplay() {
      // 获取当前选中的场景
      const selectedScene = document.querySelector('input[name="tool1"]:checked').value;

      // 遍历所有类别列表，显示与当前场景匹配的列表
      categoryLists.forEach(list => {
        if (list.getAttribute('data-scene') === selectedScene) {
          list.style.display = 'block'; // 显示匹配的场景
        } else {
          list.style.display = 'none'; // 隐藏其他场景
        }
      });
    }

    // 监听场景切换
    sceneRadios.forEach(radio => {
      radio.addEventListener('change', updateCategoryDisplay);
    });

    // 监听全选按钮（统一处理所有全选按钮）
    document.querySelectorAll('[id^="select-all_"]').forEach(selectAllCheckbox => {
      selectAllCheckbox.addEventListener('change', function () {
        // 获取对应的场景类型
        const sceneType = this.closest('.category-list').dataset.scene;

        // 获取当前场景下的所有复选框
        const checkboxes = document.querySelectorAll(`
          .category-list[data-scene="${sceneType}"]
          .target-checkbox:not([value="all"])
        `);

        // 批量设置选中状态
        checkboxes.forEach(checkbox => (checkbox.checked = this.checked));
      });
    });

    // 获取选中的类别
    function getSelectedCategories() {
      // 获取当前选中的场景
      const selectedScene = document.querySelector('input[name="tool1"]:checked').value;

      // 获取当前场景下的所有复选框
      const targetCheckboxes = document.querySelectorAll(`
        .category-list[data-scene="${selectedScene}"]
        .target-checkbox:checked
      `);

      // 获取当前场景下的“全选”复选框
      const selectAllCheckbox = document.querySelector(`
        .category-list[data-scene="${selectedScene}"]
        input[type="checkbox"][value="all"]:checked
      `);

      const selectedCategories = [];

      if (selectAllCheckbox) {
        // 如果“全选”被选中，返回当前场景下的所有类别
        document.querySelectorAll(`
          .category-list[data-scene="${selectedScene}"]
          .target-checkbox
        `).forEach(checkbox => {
          selectedCategories.push(checkbox.value);
        });
      } else {
        // 否则，只返回用户选中的类别
        targetCheckboxes.forEach(checkbox => {
          selectedCategories.push(checkbox.value);
        });
      }

      return selectedCategories;
    }


    async function performDetection() {
        if (!hasImage) {
          alert("请先上传图片！");
          return;
        }
        const file = fileInput.files[0];
        let formData = new FormData();
        formData.append("image", file);
        formData.append("conf_threshold", confThreshold.value);
        formData.append("show_confidence", document.getElementById('show-confidence-switch').checked ? "true" : "false");
	    formData.append("show_class", document.getElementById('show-class-switch').checked ? "true" : "false");
	    formData.append("save_project", document.getElementById('save-project-switch').checked ? "true" : "false");
        formData.append("scenario", getSelectedRadioValue('tool1'));
        formData.append("lightweight", getSelectedRadioValue('tool2'));
        formData.append("model_scale", getSelectedRadioValue('scale'));

        const selectedTargets = getSelectedCategories();
        if (selectedTargets.length === 0) {
            alert('请先选择需要检测的类别');
            return;
        }
        formData.append("target_type", JSON.stringify(selectedTargets));

        const projectName = document.getElementById('project-name').value.trim();
        if (projectName){
            formData.append("project_name", projectName);
            console.log(projectName);
        }

        detectionResultContainer.innerHTML = "<p>正在检测，请稍候...</p>";
        console.log("开始发送检测请求...");

        for (const [key, value] of formData.entries()) {
            console.log(key, value);
        }

        try {
          const csrfToken = getCSRFToken();
          const response = await fetch('/detect/image', {
              method: "POST",
              headers: {
                  'X-CSRF-TOKEN': csrfToken  // 只设置 CSRF Token
              },
              body: formData  // FormData
          });

          const result = await response.json();
          const detectedResult = result.detectedResult
          if (result.re_code === RET.OK) {
             const detectedImg = new Image();
             detectedImg.src = detectedResult.url;
             detectedImg.onload = function () {
                detectionResultContainer.innerHTML = '';
                detectionResultContainer.appendChild(detectedImg);
             }
             totalContainer.textContent = detectedResult.ob_counts;
             timeContainer.textContent = detectedResult.consumption_time;

             const formContent = document.getElementById('form-content');
             // 直接解析数据并插入表格行
             detectedResult.objects.forEach((obj, index) => {
               const row = document.createElement('tr');
               row.innerHTML = `
                 <td>${index + 1}</td>
                 <td>${obj.cls}</td>
                 <td>(${obj.coordinates.join(', ')})</td>
                 <td>${(obj.conf * 100).toFixed(2)}%</td>
               `;
               formContent.appendChild(row);
             });
             if (projectName){
                showAlert("检测成功", '数据正在上传中', 'success');
             }else{
                showAlert("检测成功", '检测结果正在飞速赶来', 'success');
             }
             projectName = none
          }
          else{
              detectionResultContainer.innerHTML = "<p>检测失败，请重试</p>";
              showAlert("检测失败", '请重新尝试或联系管理员', 'error');
              projectName = none
          }
          saveProjectSwitch.checked = false;
        } catch (error) {
          console.error("请求失败:", error);
          // detectionResultContainer.innerHTML = "<p>请求失败，请检查后端服务是否运行！</p>";
          projectName=none
        }
    }

    detectButton.addEventListener('click', performDetection);
