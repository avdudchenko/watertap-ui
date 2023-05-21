export const getDiagram = (id) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/'+id+'/diagram', {mode: 'cors'});
}; 