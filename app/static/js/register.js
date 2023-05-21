const registerSubmit = (event) =>{
  event.preventDefault();
  const __input = document.querySelectorAll(`form .inputBox input`)
  const submitData = new Object();
  __input.forEach((_input)=>{
    const dataKey = _input.id.split('input')[1].toLocaleLowerCase()
    submitData[dataKey] = _input.value;
  })
  postApiHasHeader('/register', JSON.stringify(submitData), callbackFun);
}

const callbackFun = (data) => {
  console.log("register_data",data)
  const contents = data['contents']
  const url = data['url']
  window.location.href = '/pop_up?contents='+contents+"&url="+url

};