import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { AdminGroupsComponent } from './groups.component';

describe('AdminGroupsComponent', () => {
  let component: AdminGroupsComponent;
  let fixture: ComponentFixture<AdminGroupsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        AdminGroupsComponent,
        HttpClientTestingModule
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AdminGroupsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
