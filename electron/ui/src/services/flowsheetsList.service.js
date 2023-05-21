export const getFlowsheetsList = () => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/',{mode: 'cors'});

    /*return new Promise((resolve, reject) => { 
        resolve(rows);
    });
    */
}; 