export const getFlowsheetsList = () => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/',{mode: 'cors'});

    /*return new Promise((resolve, reject) => { 
        resolve(rows);
    });
    */
};

export const uploadFlowsheet = (data) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/upload_flowsheet', {
        method: 'POST', 
        mode: 'cors',
        body: data
    });
}; 

export const deleteFlowsheet = (id) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/'+id+'/remove_flowsheet', {
        method: 'POST',
        mode: 'cors'
    });
}; 