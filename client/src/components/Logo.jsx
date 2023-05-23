import logo from '../assets/logo.png';
import './Style.css';

export function LogoComponent() {
    return (
        <div className='logo-container'>
            <img className='logo-img' src={logo} alt="" />
            <div className='logo-header'>SearchReduce</div>
        </div>
    );
}