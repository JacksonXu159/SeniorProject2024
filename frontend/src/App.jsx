import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { Box, Button, Typography } from '@mui/material'

function App() {
  return (
   <Box sx={{color: 'black', backgroundColor: 'white'}}>
    <Typography variant='h1'>Hello world!</Typography>
    <Button variant='contained' color='primary'>Hi there</Button>
   </Box>
  )
}

export default App
