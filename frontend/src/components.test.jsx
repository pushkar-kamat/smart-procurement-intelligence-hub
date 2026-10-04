import React from 'react';
import {describe,it,expect} from 'vitest';
import {render,screen} from '@testing-library/react';
import {MemoryRouter,Routes,Route} from 'react-router-dom';
import {Protected,RoleAction,ComparisonMatrix,validateRequisition} from './components';
describe('critical procurement UI',()=>{
 it('redirects unauthenticated access to login',()=>{render(<MemoryRouter initialEntries={['/private']}><Routes><Route path="/private" element={<Protected user={null}>Secret</Protected>}/><Route path="/login" element={<p>Sign in first</p>}/></Routes></MemoryRouter>);expect(screen.getByText('Sign in first')).toBeInTheDocument();expect(screen.queryByText('Secret')).toBeNull()});
 it('shows protected content after authentication',()=>{render(<Protected user={{id:1}}>Workspace</Protected>);expect(screen.getByText('Workspace')).toBeInTheDocument()});
 it('hides procurement actions from requester',()=>{render(<RoleAction user={{role:'requester'}} roles={['procurement']}><button>Issue PO</button></RoleAction>);expect(screen.queryByText('Issue PO')).toBeNull()});
 it('shows actions to the permitted role',()=>{render(<RoleAction user={{role:'procurement'}} roles={['procurement']}><button>Issue PO</button></RoleAction>);expect(screen.getByText('Issue PO')).toBeInTheDocument()});
 it('rejects negative requisition values before submission',()=>{expect(validateRequisition({title:'Laptop',justification:'Replace old machines',items:[{item_name:'Laptop',category:'IT',unit:'piece',quantity:-1,estimated_unit_price:50}]})).toContain('positive')});
 it('renders anomaly and risk reasons in comparison',()=>{render(<ComparisonMatrix data={{lowest_total:100,items:[{id:1,item_name:'Laptop',quantity:1,unit:'piece'}],quotations:[{id:1,vendor:{name:'Cedar'},grand_total:100,subtotal:100,tax_total:0,discount_total:0,delivery_days:5,documents:[],items:[{requisition_item_id:1,unit_price:100,analysis:{status:'FLAGGED',reason:'Above historical median',sample_count:8}}],risk:{band:'High',score:70,factors:[{factor:'late_delivery',rate_percent:90,contribution:27}]}}]}}/>);expect(screen.getByText('FLAGGED')).toBeInTheDocument();expect(screen.getByText('High')).toBeInTheDocument();expect(screen.getByText('Above historical median')).toBeInTheDocument();expect(screen.getByText('Lowest total')).toBeInTheDocument()});
});
