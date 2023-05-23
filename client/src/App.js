import { useEffect, useState } from 'react';
import { getStatistics } from './api/get_statistics';
import './App.css';
import { Document } from './components/Document';
import { Fab } from './components/Fab';
import { LogoComponent } from './components/Logo';
import { SearchBar } from './components/SearchBar';
import { StatisticsCard } from './components/StatisticsCart';
import Modal from 'react-modal';
import React from 'react';

const customStyles = {
  content: {
    top: '50%',
    left: '50%',
    right: 'auto',
    bottom: 'auto',
    marginRight: '-50%',
    transform: 'translate(-50%, -50%)',
    width: '80%',
    height: '90%',
  },
};

Modal.setAppElement('#root');

function App() {
  const [modalIsOpen, setIsOpen] = useState(false);
  const [documents, setDocuments] = useState([]);
  // const [relevants, setRelevants] = useState([
  //   {
  //     name: '1847528298285_Experiment_1',
  //     extension: 'pdf',
  //   },
  // ]);
  const [statistics, setStatistics] = useState();
  const [openDoc, setOpenDoc] = useState();

  async function getInitialData() {
    const response = await getStatistics();
        if (response) {
            const stats = response.stats;
            const docs = response.s3_docs;
            setStatistics(stats);
            setDocuments(docs);
        }
}

  useEffect(() => {
    getInitialData();
  }, []);

  return (
    <div className="App">
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={() => setIsOpen(false)}
        style={customStyles}>
        <div className='modal-header-row'>
          <div className='modal-header'>{openDoc}</div>
          <div className='modal-close-button' onClick={() => {
            setIsOpen(false);
            setOpenDoc(null);
          }}>❌</div>
        </div>
        <iframe width="100%" height="100%" frameBorder="0" src={`https://docs.google.com/gview?url=https://eccproject-iub.s3.amazonaws.com/${openDoc}&embedded=true`}></iframe>
      </Modal>
      <Fab getNewData={getInitialData} />
      <div className='left-container'>
        <LogoComponent />
        <StatisticsCard statistics={statistics} />
      </div>
      <div className='right-container'>
        <SearchBar onSearchResults={setDocuments} />
        <div className='section-title'>Files</div>
        <div className='documents-container'>
          {
            documents.map((document) => <Document key={document.name} name={document.name} extension={document.extension} onClick={() => {
              setOpenDoc(document.name + "." + document.extension);
              setIsOpen(true);
            }} />)
          }
        </div>
        {/* <div className='section-title'>Relevant Files</div>
        <div className='documents-container'>
          {
            relevants.map((document) => <Document key={document.name} name={document.name} extension={document.extension} />)
          }
        </div> */}
      </div>
    </div>
  );
}

export default App;
