import {Routes, Route, Link } from 'react-router'
//link change the page without having to reload
// route helps us to define which component should be 
import BrowsePage from './pages/BrowsePage'
import ProductsDetailPage from './pages/ProductsDetailPage'
import ProductsPage from  './pages/ProductsPage'

function App() {
 return(
    <>
    <nav>
      <Link to="/">All Products</Link> | <Link to="/browse">Browse</Link>
    </nav>
    <Routes>
      <Route path="/" element= {<ProductsPage/>}/>
      <Route path="/browse" element= {<BrowsePage/>}/>
      <Route path="/products/:id" element= {<ProductsDetailPage/>}/>
      <Route path="*" element={<h1> 404 Not Found</h1>}></Route>
    </Routes>
    
    </>
  )
}

export default App