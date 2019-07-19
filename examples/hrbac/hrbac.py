# -*- generated by 1.1.0b13 -*-
import da
_config_object = {}
import time
import sys, os
import argparse
import cProfile
import gc
gc.disable()

class CoreRBAC(da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def setup(self, _users, _roles, _ur, **rest_1571):
        super().setup(_users=_users, _roles=_roles, _ur=_ur, **rest_1571)
        self._state._users = _users
        self._state._roles = _roles
        self._state._ur = _ur
        self._state.USERS = self._state._users
        self._state.ROLES = self._state._roles
        self._state.PERMS = set()
        self._state.UR = self._state._ur
        self._state.PR = set()

    def AddUser(self, user):
        self._state.USERS.add(user)

    def DeleteUser(self, user):
        self._state.UR -= {(user, r) for r in self._state.ROLES}
        self._state.USERS.remove(user)

    def AddRole(self, role):
        self._state.ROLES.add(role)

    def DeleteRole(self, role):
        self._state.UR -= {(u, role) for u in self._state.USERS}
        self._state.PR -= {(p, role) for p in self._state.PERMS}
        self._state.ROLES.remove(role)

    def AddPerm(self, perm):
        self._state.PERMS.add(perm)

    def DeletePerm(self, perm):
        self._state.PR -= {(perm, r) for r in self._state.ROLES}
        self._state.PERMS.remove(perm)

    def AddUR(self, user, role):
        self._state.UR.add((user, role))

    def DeleteUR(self, user, role):
        self._state.UR.remove((user, role))

    def AddPR(self, perm, role):
        self._state.PR.add((perm, role))

    def DeletePR(self, perm, role):
        self._state.PR.remove((perm, role))

    def AssignedUsers(self, role):
        'the set of users assigned to role in UR'
        return {u for (u, _BoundPattern379_) in self._state.UR if (_BoundPattern379_ == role)}

    def AssignedRoles(self, user):
        'the set of roles assigned to user in UR'
        return {r for (_BoundPattern392_, r) in self._state.UR if (_BoundPattern392_ == user)}

    def UserPermissions(self, user):
        'the set of permissions assigned to the roles assigned to user'
        return {p for (_BoundPattern407_, r) in self._state.UR if (_BoundPattern407_ == user) for (p, _FreePattern416_) in self._state.PR if (_FreePattern416_ == r)}

class HierarchicalRBAC(CoreRBAC, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def setup(self, _users, _roles, _ur, _rh, _workload, _outfile, **rest_1571):
        super().setup(_users=_users, _roles=_roles, _ur=_ur, _rh=_rh, _workload=_workload, _outfile=_outfile, **rest_1571)
        self._state._users = _users
        self._state._roles = _roles
        self._state._ur = _ur
        self._state._rh = _rh
        self._state._workload = _workload
        self._state._outfile = _outfile
        super().setup(self._state._users, self._state._roles, self._state._ur)
        self._state.RH = self._state._rh
        self._state.workload = self._state._workload
        self._state.outfile = self._state._outfile

    def run(self):
        (utime1, stime1, cutime1, cstime1, elapsed_time1) = os.times()
        for (op, pr) in self._state.workload:
            if (op in {'AddUser', 'DeleteUser', 'AddRole', 'DeleteRole', 'AuthorizedUsers'}):
                for i in pr:
                    eval(('self.' + op))(i)
            else:
                for (i, j) in pr:
                    eval(('self.' + op))(i, j)
        (utime, stime, cutime, cstime, elapsed_time) = os.times()
        fout = open(self._state.outfile, 'a')
        fout.write((((str((elapsed_time - elapsed_time1)) + ',') + str((((((((utime - utime1) + stime) - stime1) + cutime) - cutime1) + cstime) - cstime1))) + '\n'))
        fout.close()

    def AddInheritance(self, a, d):
        self._state.RH.add((a, d))

    def DeleteInheritance(self, a, d):
        self._state.RH.remove((a, d))

    def AuthorizedUsers(self, _role):
        'the set of users of role or ascendant roles of role'
        transRH = self.trans(self._state.RH)
        return {u for (u, asc) in self._state.UR for (_FreePattern507_, _BoundPattern509_) in transRH if (_FreePattern507_ == asc) if (_BoundPattern509_ == role)}

    def trans(self, E):
        pass
        '\n    for input using keyword arguments:\n    if keyword arguments are given, use the given arguments as input,\n    otherwise if named attributes are defined, use defined attributes ?\n    otherwise, use empty sets ?  no, treat as undefined\n    for output using non-keyword arguments:\n    if non-keyward arguments are given, return a set of tuples for each arg,\n    otherwise, write to named attributes of the inferred sets of tuples\n    '

class HRBAC_py(HierarchicalRBAC, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def trans(self, E):
        T = E
        W = ({(x, d) for (x, y) in T for (a, d) in E if (y == a)} - T)
        while W:
            T.add(W.pop())
            W = ({(x, d) for (x, y) in T for (a, d) in E if (y == a)} - T)
        return (T | {(r, r) for r in self._state.ROLES})

    def AuthorizedUsers(self, role):
        transRH = self.trans(self._state.RH)
        user = self._state.USERS
        roles = self._state.ROLES
        ur = self._state.UR
        return set((u for u in user for asc in roles if (((asc, role) in transRH) and ((u, asc) in ur))))

class HRBAC_set(HierarchicalRBAC, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def trans(self, E):
        'the transitive closure of role hierarchy E union reflexive role pairs\n    '
        T = E
        z = y = x = None

        def ExistentialOpExpr_791():
            nonlocal z, y, x
            for (x, y) in T:
                for (_FreePattern802_, z) in E:
                    if (_FreePattern802_ == y):
                        if (not ((x, z) in T)):
                            return True
            return False
        while ExistentialOpExpr_791():
            T.add((x, z))
        return (T | {(r, r) for r in self._state.ROLES})

    def AuthorizedUsers(self, role):
        'the set of users of role or ascendant roles of role'
        transRH = self.trans(self._state.RH)
        return {u for (u, asc) in self._state.UR for (_FreePattern857_, _BoundPattern858_) in transRH if (_FreePattern857_ == asc) if (_BoundPattern858_ == role)}

    def AuthorizedRoles(self, user):
        'the set of roles of user or descendant roles of the roles'
        self._state.transRH = self.trans(self._state.RH)
        return {r for (_BoundPattern879_, asc) in self._state.UR if (_BoundPattern879_ == user) for (_FreePattern886_, r) in self._state.transRH if (_FreePattern886_ == asc)}

class HRBAC_set_maint(HRBAC_set, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def setup(self, _users, _roles, _ur, _rh, _workload, _outfile, **rest_1571):
        super().setup(_users=_users, _roles=_roles, _ur=_ur, _rh=_rh, _workload=_workload, _outfile=_outfile, **rest_1571)
        self._state._users = _users
        self._state._roles = _roles
        self._state._ur = _ur
        self._state._rh = _rh
        self._state._workload = _workload
        self._state._outfile = _outfile
        super().setup(self._state._users, self._state._roles, self._state._ur, self._state._rh, self._state._workload, self._state._outfile)
        self._state.transRH = self.trans(self._state._rh)

    def AddInheritance(self, a, d):
        super().AddInheritance(a, d)
        self._state.transRH = self.trans(self._state.RH)

    def DeleteInheritance(self, a, d):
        super().DeleteInheritance(a, d)
        self._state.transRH = self.trans(self._state.RH)

    def AuthorizedUsers(self, role):
        return set((u for u in self._state.USERS for asc in self._state.ROLES if (((asc, role) in self._state.transRH) and ((u, asc) in self._state.UR))))

class HRBAC_transRH_rules(HRBAC_set_maint, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def setup(self, _users, _roles, _ur, _rh, _workload, _outfile):
        super().setup(_users, _roles, _ur, _rh, _workload, _outfile)
        self._rules_object = {'HRBAC_transRH_rules': {'LhsVars': {('transRH', 2)}, 'RhsVars': {}, 'Unbounded': {'roles', 'rh'}, 'UnboundedLeft': {}}}

    def AddInheritance(self, a, d):
        super().AddInheritance(a, d)
        self._state.transRH = self.infer([('rh', self._state.RH), ('roles', self._state.ROLES)], ['transRH(_,_)'], 'HRBAC_transRH_rules')

    def DeleteInheritance(self, a, d):
        super().DeleteInheritance(a, d)
        self._state.transRH = self.infer([('rh', self._state.RH), ('roles', self._state.ROLES)], ['transRH(_,_)'], 'HRBAC_transRH_rules')

class HRBAC_transRH_rs(HierarchicalRBAC, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def setup(self, _users, _roles, _ur, _rh, _workload, _outfile, **rest_1571):
        super().setup(_users=_users, _roles=_roles, _ur=_ur, _rh=_rh, _workload=_workload, _outfile=_outfile, **rest_1571)
        self._state._users = _users
        self._state._roles = _roles
        self._state._ur = _ur
        self._state._rh = _rh
        self._state._workload = _workload
        self._state._outfile = _outfile
        super().setup(self._state._users, self._state._roles, self._state._ur, self._state._rh, self._state._workload, self._state._outfile)
        self._state.transRH = None
        self._rules_object = {'HRBAC_transRH_rs': {'LhsVars': {('transRH', 2)}, 'RhsVars': {'RH', 'ROLES'}, 'Unbounded': {}, 'UnboundedLeft': {}}}
        self._state.transRH = self.infer(rule='HRBAC_transRH_rs', queries=['transRH(_,_)'])

    def AuthorizedUsers(self, role):
        return {u for (u, asc) in self._state.UR for (_FreePattern1073_, _BoundPattern1074_) in self._state.transRH if (_FreePattern1073_ == asc) if (_BoundPattern1074_ == role)}

    def AddInheritance(self, a, d):
        super().AddInheritance(a, d)
        self._state.transRH = self.infer(rule='HRBAC_transRH_rs', queries=['transRH(_,_)'])

    def DeleteInheritance(self, a, d):
        super().DeleteInheritance(a, d)
        self._state.transRH = self.infer(rule='HRBAC_transRH_rs', queries=['transRH(_,_)'])

    def AddRole(self, role):
        super().AddRole(role)
        self._state.transRH = self.infer(rule='HRBAC_transRH_rs', queries=['transRH(_,_)'])

    def DeleteRole(self, role):
        super().DeleteRole(role)
        self._state.transRH = self.infer(rule='HRBAC_transRH_rs', queries=['transRH(_,_)'])

class HRBAC_trans_rules(HRBAC_py, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def setup(self, _users, _roles, _ur, _rh, _workload, _outfile):
        super().setup(_users, _roles, _ur, _rh, _workload, _outfile)
        self._rules_object = {'HRBAC_trans_rules': {'LhsVars': {}, 'RhsVars': {}, 'Unbounded': {'edge'}, 'UnboundedLeft': {('path', 2)}}}

    def trans(self, E):
        i = self.infer([('edge', E)], ['path'], 'HRBAC_trans_rules')
        return (set(i) | {(r, r) for r in self._state.ROLES})

class HRBAC_trans_rules_all(HRBAC_py, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def setup(self, _users, _roles, _ur, _rh, _workload, _outfile):
        super().setup(_users, _roles, _ur, _rh, _workload, _outfile)
        self._rules_object = {'HRBAC_trans_rules_all': {'LhsVars': {}, 'RhsVars': {}, 'Unbounded': {'edge', 'ur'}, 'UnboundedLeft': {('path', 2), ('authuser', 2)}}}

    def AuthorizedUsers(self, role):
        i = self.infer([('edge', self._state.RH), ('ur', self._state.UR)], ['authuser(_,{ROLE})'.format(ROLE=role)])
        return (set(i) | {(u,) for (u, _BoundPattern1145_) in self._state.UR if (_BoundPattern1145_ == role)})

class HRBAC_trans_with_role_rules(HRBAC_py, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def setup(self, _users, _roles, _ur, _rh, _workload, _outfile):
        super().setup(_users, _roles, _ur, _rh, _workload, _outfile)
        self._rules_object = {'trans_with_role_rules': {'LhsVars': {}, 'RhsVars': {}, 'Unbounded': {'role', 'edge'}, 'UnboundedLeft': {('path', 2)}}}

    def trans(self, E):
        return self.infer([('edge', E), ('role', self._state.ROLES)], ['path(_,_)'], 'trans_with_role_rules')

class HRBAC_trans_with_role_rules_all(HRBAC_py, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def setup(self, _users, _roles, _ur, _rh, _workload, _outfile):
        super().setup(_users, _roles, _ur, _rh, _workload, _outfile)
        self._rules_object = {'HRBAC_trans_with_role_rules_all': {'LhsVars': {}, 'RhsVars': {}, 'Unbounded': {'edge', 'roles', 'ur'}, 'UnboundedLeft': {('path', 2), ('authuser', 2)}}}

    def AuthorizedUsers(self, role):
        return self.infer([('edge', self._state.RH), ('roles', self._state.ROLES), ('ur', self._state.UR)], ['authuser(_,{})'.format(role)], 'HRBAC_trans_with_role_rules_all')

class HRBAC_trans_with_ROLES_rules(HRBAC_set, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def setup(self, _users, _roles, _ur, _rh, _workload, _outfile):
        super().setup(_users, _roles, _ur, _rh, _workload, _outfile)
        self._rules_object = {'trans_with_ROLES_rules': {'LhsVars': {}, 'RhsVars': {'ROLES'}, 'Unbounded': {'edge'}, 'UnboundedLeft': {('path', 2)}}}

    def trans(self, E):
        return self.infer([('edge', E)], ['path(_,_)'])

class HRBAC_transRH_with_edge_rules(HRBAC_set, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def setup(self, _users, _roles, _ur, _rh, _workload, _outfile):
        super().setup(_users, _roles, _ur, _rh, _workload, _outfile)
        self._rules_object = {'transRH_with_edge_rules': {'LhsVars': {('transRH', 2)}, 'RhsVars': {'ROLES'}, 'Unbounded': {'edge'}, 'UnboundedLeft': {}}}

    def trans(self, E):
        pass

class HRBAC_trans_with_RH_ROLES_rules(HRBAC_set, da.DistProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])

    def setup(self, _users, _roles, _ur, _rh, _workload, _outfile):
        super().setup(_users, _roles, _ur, _rh, _workload, _outfile)
        self._rules_object = {'trans_with_RH_ROLES_rules': {'LhsVars': {}, 'RhsVars': {'RH', 'ROLES'}, 'Unbounded': {}, 'UnboundedLeft': {('path', 2)}}}

    def trans(self, E):
        return self.infer(queries=['path(_,_)'], rules=trans_with_RH_ROLES_rules)

class Node_(da.NodeProcess):

    def __init__(self, procimpl, forwarder, **props):
        super().__init__(procimpl, forwarder, **props)
        self._events.extend([])
    _config_object = {'channel': 'fifo', 'clock': 'lamport'}

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--numr', type=int, default=100)
        parser.add_argument('--numq', type=int, default=50)
        parser.add_argument('--q', type=int, default=50)
        parser.add_argument('--mode', type=str, default='RHrule')
        args = parser.parse_args()
        print(f'========================================================\n r: {args.numr} q: {args.numq} auth: {args.q} mode: {args.mode} \n========================================================')
        users = set(range((10 * args.numr)))
        roles = set(range(args.numr))
        rh = eval(open((('./input/HR_' + str(args.numr)) + '.py')).read())
        ur = eval(open((('./input/UR_' + str(args.numr)) + '.py')).read())
        workload = eval(open((((((('./input/hrbacSequence_r' + str(args.numr)) + '_q') + str(args.numq)) + '_auth') + str(args.q)) + '.py')).read())
        outfile = ((((((((('./timing/timing_hrbac_' + args.mode) + '_') + 'r') + str(args.numr)) + '_q') + str(args.numq)) + '_auth') + str(args.q)) + '.txt')
        if (not os.path.exists('timing')):
            os.mkdir('timing')
        if (args.mode == 'python'):
            o = self.new(HRBAC_py, [users, roles, ur, rh, workload, outfile])
        elif (args.mode == 'distalgo'):
            o = self.new(HRBAC_set, [users, roles, ur, rh, workload, outfile])
        elif (args.mode == 'RHrule'):
            o = self.new(HRBAC_transRH_rules, [users, roles, ur, rh, workload, outfile])
        elif (args.mode == 'rule'):
            o = self.new(HRBAC_trans_rules, [users, roles, ur, rh, workload, outfile])
        elif (args.mode == 'rule_all'):
            o = self.new(HRBAC_trans_rules_all, [users, roles, ur, rh, workload, outfile])
        elif (args.mode == 'rolerule'):
            o = self.new(HRBAC_trans_with_role_rules, [users, roles, ur, rh, workload, outfile])
        elif (args.mode == 'rolerule_all'):
            o = self.new(HRBAC_trans_with_role_rules_all, [users, roles, ur, rh, workload, outfile])
        elif (args.mode == 'transRH'):
            o = self.new(HRBAC_transRH_rs, [users, roles, ur, rh, workload, outfile])
        else:
            print('no such mode')
            sys.exit()
        self._start(o)
