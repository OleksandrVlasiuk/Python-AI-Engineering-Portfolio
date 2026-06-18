import React, { useState, useEffect } from 'react';
import api from '../API';
import Cookies from 'js-cookie';
import configData from '../config.json';

const Home = () => {
  const [transactions, setTransactions] = useState([]);
  const [formData, setFormData] = useState({
    string: '',
    is_encode: true,
  });

  const [showLongTextMessage, setShowLongTextMessage] = useState(false);
  const [showEncodingErrorMessage, setShowEncodingErrorMessage] = useState(false);

  // Function to handle refreshing the access token
  const refreshAccessToken = async () => {
    try {
      const refreshToken = Cookies.get('refresh_token'); // Get the refresh token
      const response = await api.post('/refresh', { refresh_token: refreshToken });

      if (response.data && response.data.access_token) {
        // Update the stored access token
        Cookies.set('access_token', response.data.access_token);
      }
    } catch (error) {
      console.error('Failed to refresh access token', error);
    }
  };

  const fetchTransactions = async () => {
    const accessToken = Cookies.get('access_token');
    const config = {
      headers: {
        Authorization: accessToken,
      },
    };

    try {
      const response = await api.get('/gettasks/', config);
      setTransactions(response.data);
    } catch (error) {
      console.error('Failed to fetch transactions', error);

      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        // Access token has expired, try refreshing it
        refreshAccessToken();
      }
    }
  };

  useEffect(() => {
    fetchTransactions(); // Fetch data when the component loads

    // Set up an interval to refresh data every one second (1000 milliseconds)
    const intervalId = setInterval(() => {
      fetchTransactions();
    }, 2000);

    // Clear the interval when the component unmounts
    return () => {
      clearInterval(intervalId);
    };
  }, []); // The empty dependency array ensures this runs once on mount

  const handleInputChange = (event) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;

    if (value.length > configData.maxNumber) {
      setShowLongTextMessage(true);
    } else {
      setShowLongTextMessage(false);
    }

    setFormData({
      ...formData,
      [event.target.name]: value,
    });
  };

  const handleFormSubmit = async (event) => {
    event.preventDefault();

    if (formData.string.length > configData.maxNumber) {
      setShowLongTextMessage(true);
      return;
    }

    const accessToken = Cookies.get('access_token');
    const config = {
      headers: {
        Authorization: accessToken,
      },
    };

    try {
      const response = await api.post('/createtask/', formData, config);
      fetchTransactions(); // Refresh data after creating a task
      setFormData({
        string: '',
        is_encode: true,
      });

      if (response.data.accepted === false) {
        setShowEncodingErrorMessage(true);

        setTimeout(() => {
          setShowEncodingErrorMessage(false);
        }, 3000);
      }
    } catch (error) {
      console.error('Failed to create task', error);
    }
  };

  const handleCancelClick = async (taskId) => {
    const accessToken = Cookies.get('access_token');
    const config = {
      method: 'PUT', // Use the PUT method for updating the task
      headers: {
        'Authorization': accessToken,
        'Content-Type': 'application/json', // Set the content type
      },
    };
  
    try {
      const response = await api.put(`/canceltask?task_id=${taskId}`, config);
  
      if (response.ok) {
        // Request was successful, update the task status in your state
        const updatedTransactions = [...transactions];
        const canceledTaskIndex = updatedTransactions.findIndex(task => task.id === taskId);
        
        if (canceledTaskIndex !== -1) {
          updatedTransactions[canceledTaskIndex].status = "Cancelled";
          setTransactions(updatedTransactions);
        }
      } else {
        // Handle error if the request was not successful
        console.error('Failed to cancel the task');
      }
    } catch (error) {
      console.error('Error during cancel request', error);
    }
  };

  const handleDownloadClick = (taskId) => {
    const accessToken = Cookies.get('access_token');
    const config = {
      headers: {
        'Authorization': accessToken,
      },
      responseType: 'blob',
    };
  
    api.get(`/downloadtask?task_id=${taskId}`, config)
      .then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'result.txt');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      })
      .catch((error) => {
        console.error(error);
      });
  };
   
  return (
    <div>
      <nav className='navbar navbar-dark bg-primary'>
        <div className='container-fluid'>
          <a className='navbar-brand' href="#"> Encode Your Text </a>
        </div>
      </nav>

      <div className='container'>
        <form onSubmit={handleFormSubmit}>
          <div className='mb-3 mt-3'>
            <label htmlFor='amount' className='form-label'>
              Text
            </label>
            <input
              type='text'
              className='form-control'
              id='string'
              name='string'
              onChange={handleInputChange}
              value={formData.string}
            />
          </div>

          <div className='mb-3'>
            <label htmlFor='is_encode' className='form-label'>
              Encode?
            </label>
            <input
              type='checkbox'
              id='is_encode'
              name='is_encode'
              onChange={handleInputChange}
              value={formData.is_encode}
              checked={true}
              disabled
            />
          </div>

          <button type='submit' className='btn btn-primary'>
            Submit
          </button>
        </form>

        {showLongTextMessage && (
          <div className="alert alert-danger" role="alert">
            The text is too long
          </div>
        )}
        {showEncodingErrorMessage && (
          <div className="alert alert-danger" role="alert">
            The text cannot be encoded
          </div>
        )}

        <table className='table table-striped table-bordered table-hover'>
          <thead>
            <tr>
              <th>Status</th>
              <th>Start Time</th>
              <th>Finish Time</th>
              <th>Cancel</th>
              <th>Download</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((transaction) => (
              <tr key={transaction.id}>
                <td>{transaction.status}</td>
                <td>{transaction.start_time}</td>
                <td>{transaction.finish_time}</td>
                <td>
                  {transaction.status.startsWith("In progress") ? (
                    <button
                      className="btn btn-link"
                      onClick={() => handleCancelClick(transaction.id)}
                    >
                      <i>Cancel</i>
                    </button>
                  ) : (
                    <div></div>
                  )}
                </td>
                <td>
                  {/* <button
                    className="btn btn-link"
                    onClick={() => handleDownloadClick(transaction.id)}
                  >
                    <i>Download</i>
                  </button> */}
                  {transaction.status === "Finished" ? (
                    <button
                      className="btn btn-link"
                      onClick={() => handleDownloadClick(transaction.id)}
                    >
                      <i>Download</i>
                    </button>
                  ) : (
                    <div></div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Home;