import Http from './http'

const http = new Http()

const models = ['brand', 'category']

const requesetBrandData = () => {
  const path = `/brand/`

  return http.get(path)
}

const requesetCategoryData = () => {
  const path = `/category/`

  return http.get(path)
}

const editData = (model, data) => {
  let path = ''
  if (models.includes(model)) {
    path = `/${model}/${data.id}/`
    return http.put(path, data)
  }

  console.error('错误的请求!')
  return false
}

const deleteData = (model, id) => {
  let path = ''
  if (models.includes(model)) {
    path = `${model}/${id}/`
    return http.delete(path)
  }

  console.error('错误的请求!')
  return false
}

const createData = (model, data) => {
  let path = ''
  if (models.includes(model)) {
    path = `/${model}/`
    return http.post(path, data)
  }

  console.error('错误的请求!')
  return false
}

export default { requesetBrandData, requesetCategoryData, editData, deleteData, createData }
